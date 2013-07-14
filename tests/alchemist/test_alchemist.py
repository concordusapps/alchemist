# -*- coding: utf-8 -*-
import sys
import os
from alchemist import Alchemist


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

    def test_package(self):
        from a import application

        assert application.config['SECRET'] == 'COOKIE'


class TestDatabaseUri:

    def test_name(self):
        uri = Alchemist._build_database_uri(
            engine='sqlite',
            name=':memory:')

        assert uri == 'sqlite:///:memory:'

    def test_test(self):
        uri = Alchemist._build_database_uri(
            testing=True,
            engine='sqlite',
            name='real_db',
            test_name=':memory:')

        assert uri == 'sqlite:///:memory:'

    def test_user_pass(self):
        uri = Alchemist._build_database_uri(
            engine='postgresql',
            user='bob',
            port=5432,
            name='example', **{'pass': 'b'})

        assert uri == 'postgresql:///bob:b@localhost:5432/example'

    def test_user_pass_test(self):
        uri = Alchemist._build_database_uri(
            testing=True,
            engine='postgresql',
            test_engine='mysql',
            username='bob',
            test_username='a',
            password='b',
            test_password='a',
            port=5432,
            test_port=1024,
            name='example')

        assert uri == 'mysql:///a:a@localhost:1024/test_example'

    def test_user(self):
        uri = Alchemist._build_database_uri(
            engine='postgresql',
            username='bob',
            port=5432,
            name='example')

        assert uri == 'postgresql:///bob@localhost:5432/example'

    def test_host(self):
        uri = Alchemist._build_database_uri(
            engine='postgresql',
            username='bob',
            port=5432,
            host='example.com',
            name='example')

        assert uri == 'postgresql:///bob@example.com:5432/example'

    def test_host_ip(self):
        uri = Alchemist._build_database_uri(
            engine='postgresql',
            username='bob',
            port=5432,
            hostname='::1',
            name='example')

        assert uri == 'postgresql:///bob@[::1]:5432/example'


class TestDatabaseEngine(BaseTest):

    def test_database(self):
        from a import application

        assert len(application.databases) == 2


class TestContext(BaseTest):

    def test_current_app(self):
        from a import application

        config = application.config
        context = application.app_context()
        context.push()

        from alchemist import application

        config == application.config

        context.pop()
