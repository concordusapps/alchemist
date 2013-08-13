# -*- coding: utf-8 -*-
from alchemist import utils


class TestDatabaseUri:

    def test_name(self):
        uri = utils.build_database_uri(
            engine='sqlite',
            name=':memory:')

        assert uri == 'sqlite:///:memory:'

    def test_test(self):
        uri = utils.build_database_uri(
            testing=True,
            engine='sqlite',
            name='real_db',
            test_name=':memory:')

        assert uri == 'sqlite:///:memory:'

    def test_user_pass(self):
        uri = utils.build_database_uri(
            engine='postgresql',
            user='bob',
            port=5432,
            name='example', **{'pass': 'b'})

        assert uri == 'postgresql://bob:b@localhost:5432/example'

    def test_user_pass_test(self):
        uri = utils.build_database_uri(
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

        assert uri == 'mysql://a:a@localhost:1024/test_example'

    def test_user(self):
        uri = utils.build_database_uri(
            engine='postgresql',
            username='bob',
            port=5432,
            name='example')

        assert uri == 'postgresql://bob@localhost:5432/example'

    def test_host(self):
        uri = utils.build_database_uri(
            engine='postgresql',
            username='bob',
            port=5432,
            host='example.com',
            name='example')

        assert uri == 'postgresql://bob@example.com:5432/example'

    def test_host_ip(self):
        uri = utils.build_database_uri(
            engine='postgresql',
            username='bob',
            port=5432,
            hostname='::1',
            name='example')

        assert uri == 'postgresql://bob@[::1]:5432/example'
