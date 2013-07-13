# -*- coding: utf-8 -*-
import sys


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
