# -*- coding: utf-8 -*-
from alchemist.test import settings
from flask import Flask
from os import path
import os
import sys
import alchemist


class TestSettings:

    def test_project(self):
        self.app = Flask('alchemist.tests.a')
        with settings(self.app):
            alchemist.configure(self.app)

            assert self.app.config.get('A_SETTING', 1)

    def test_missing_project(self):
        """
        Should succeed and not raise if the project does not contain
        a settings file.
        """

        self.app = Flask('alchemist')
        with settings(self.app):
            alchemist.configure(self.app)

    def test_component(self):
        self.app = Flask('alchemist.tests.a')
        with settings(self.app, COMPONENTS=['alchemist.tests.a.b']):
            alchemist.configure(self.app)

            assert self.app.config.get('B_SETTING', 1)
            assert self.app.config.get('A_SETTING', 5)

    def test_project_as_component(self):
        """
        Should not merge the project settings in twice even if
        it is listed in the COMPONENTS array.
        """

        self.app = Flask('alchemist.tests.a')
        components = ['alchemist.tests.a.b', 'alchemist.tests.a']
        with settings(self.app, COMPONENTS=components):
            alchemist.configure(self.app)

            assert self.app.config.get('B_SETTING', 1)
            assert self.app.config.get('A_SETTING', 5)

    def test_global_env(self):
        """
        Should override settings from the file specified in the
        ALCHEMIST_SETTINGS_MODULE environ variable.
        """

        filename = path.join(path.dirname(__file__), '../a/b/settings.py')
        os.environ['ALCHEMIST_SETTINGS_MODULE'] = filename

        self.app = Flask('alchemist.tests.a')
        with settings(self.app):
            alchemist.configure(self.app)

            assert self.app.config.get('B_SETTING', 1)
            assert self.app.config.get('A_SETTING', 5)

        del os.environ['ALCHEMIST_SETTINGS_MODULE']

    def test_project_env(self):
        """
        Should override settings from the file specified in the
        <project>_SETTINGS_MODULE environ variable.
        """

        filename = path.join(path.dirname(__file__), '../a/b/settings.py')
        os.environ['TESTS_A_SETTINGS_MODULE'] = filename

        self.app = Flask('alchemist.tests.a')
        with settings(self.app):
            alchemist.configure(self.app)

            assert self.app.config.get('B_SETTING', 1)
            assert self.app.config.get('A_SETTING', 5)

        del os.environ['TESTS_A_SETTINGS_MODULE']


class TestApplication:

    @staticmethod
    def _clear_cache():
        from alchemist import app
        type(app).__dict__['_find_application']._cache.clear()

    def setup(self):
        self._clear_cache()

    def teardown(self):
        self._clear_cache()

    def test_stack(self):
        from .a.example import application

        assert application.name == 'alchemist.tests.a'

    def test_env(self):
        os.environ['ALCHEMIST_APPLICATION'] = 'alchemist.tests.a'

        from .a.b.example import application

        assert application.name == 'alchemist.tests.a'

        del os.environ['ALCHEMIST_APPLICATION']

    def test_env_direct(self):
        os.environ['ALCHEMIST_APPLICATION'] = 'alchemist.tests.a.b'

        from alchemist.app import application

        assert application.name == 'alchemist.tests.a.b'

        del os.environ['ALCHEMIST_APPLICATION']


class TestTestingDetection:

    def setup(self):
        self.app = Flask('alchemist.tests.a')
        self.context = self.app.app_context()
        self.context.push()

    def teardown(self):
        self.context.pop()

    def test_nose(self):
        old = sys.argv
        sys.argv = ['nosetests']

        alchemist.configure(self.app)

        assert self.app.config['TESTING']

        sys.argv = old

    def test_py(self):
        old = sys.argv
        sys.argv = ['py.test']

        alchemist.configure(self.app)

        assert self.app.config['TESTING']

        sys.argv = old

    def test_unittest(self):
        old = sys.argv
        sys.argv = ['python', 'setup.py', 'test']

        alchemist.configure(self.app)

        assert self.app.config['TESTING']

        sys.argv = old

    def test_alchemist(self):
        old = sys.argv
        sys.argv = ['alchemist', 'test']

        alchemist.configure(self.app)

        assert self.app.config['TESTING']

        sys.argv = old

    def test_not(self):
        old = sys.argv
        sys.argv = ['alchemist', 'load', '../../test.py']

        alchemist.configure(self.app)

        assert not self.app.config['TESTING']

        sys.argv = old
