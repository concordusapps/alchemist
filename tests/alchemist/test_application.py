# -*- coding: utf-8 -*-
import sys
import os


class BaseTest:

    def setup(self):
        # Unload all alchemist.* modules and test packages.
        for name in list(sys.modules.keys()):
            for test in ['a', 'a.b', 'a.b.c', 'example', 'alchemist']:
                if name.startswith(test) and name in sys.modules:
                    del sys.modules[name]


class TestTestingDetection(BaseTest):

    def test_nose(self):
        old = sys.argv
        sys.argv = ['nosetests']

        from a import application

        assert application.config['TESTING']

        sys.argv = old

    def test_py(self):
        old = sys.argv
        sys.argv = ['py.test']

        from a import application

        assert application.config['TESTING']

        sys.argv = old

    def test_unittest(self):
        old = sys.argv
        sys.argv = ['python', 'setup.py', 'test']

        from a import application

        assert application.config['TESTING']

        sys.argv = old

    def test_alchemist(self):
        old = sys.argv
        sys.argv = ['alchemist', 'test']

        from a import application

        assert application.config['TESTING']

        sys.argv = old

    def test_not(self):
        old = sys.argv
        sys.argv = ['alchemist', 'load', '../../test.py']

        from a import application

        assert not application.config['TESTING']

        sys.argv = old


class TestSettingsResolution(BaseTest):

    def test_project(self):
        from a import application

        assert 'PACKAGES' in application.config
        assert application.config['PACKAGES'][0] == 'alchemist'
        assert application.config['PACKAGES'][1] == 'a.b'

    def test_env(self):
        os.environ['ALCHEMIST_SETTINGS_MODULE'] = '../alchemist_settings.py'

        from a import application

        assert application.config['ANSWER'] == 42
        assert application.config['QUESTION'] == 'Is anybody out there?'

        del os.environ['ALCHEMIST_SETTINGS_MODULE']

    def test_env_duo(self):
        os.environ['ALCHEMIST_SETTINGS_MODULE'] = '../alchemist_settings.py'
        os.environ['A_SETTINGS_MODULE'] = '../settings.py'

        from a import application

        assert application.config['ANSWER'] == application.config['QUESTION']

        del os.environ['ALCHEMIST_SETTINGS_MODULE']
        del os.environ['A_SETTINGS_MODULE']
