# -*- coding: utf-8 -*-
from alchemist.test import settings
import alchemist
from flask import Flask
import contextlib
from pytest import raises
from . import utils


class TestEngine:

    @staticmethod
    def _clear_cache():
        from alchemist.db._engine import Engine
        Engine.__getitem__._cache.clear()

    def setup(self):
        utils.unload_modules('alchemist')
        self._clear_cache()
        self.app = Flask('alchemist')
        self.context = self.app.app_context()
        self.context.push()

    def teardown(self):
        self.context.pop()
        self._clear_cache()

    def test_default_repr(self):
        from alchemist import db

        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'default': uri}):

            assert repr(db.engine) == repr(db.engine['default'])

    def test_default(self):
        from alchemist import db

        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'default': uri}):

            assert db.engine.url.drivername == 'sqlite'
            assert db.engine.url.database == ':memory:'

    def test_alternative(self):
        from alchemist import db

        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'other': uri}):

            assert db.engine['other'].url.drivername == 'sqlite'
            assert db.engine['other'].url.database == ':memory:'

    def test_missing(self):
        from alchemist import db, exceptions

        with settings(self.app):

            with raises(exceptions.ImproperlyConfigured):
                db.engine['default']

    def test_missing_database(self):
        from alchemist import db, exceptions

        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'other': uri}):

            with raises(exceptions.ImproperlyConfigured):
                db.engine['default']

    def test_usage(self):
        from alchemist import db

        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'default': uri}):

            with contextlib.closing(db.engine.connect()) as connection:

                result = connection.execute("BEGIN")
                assert result.closed

    def test_lookup(self):
        from alchemist import db

        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'default': uri}):

            assert 'connect' in dir(db.engine)

    def test_expanded(self):
        from alchemist import db

        config = {
            'engine': 'sqlite',
            'name': 'name',
        }

        with settings(self.app, DATABASES={'default': config}):

            assert db.engine.url.drivername == 'sqlite'


class TestSession:

    def setup(self):
        utils.unload_modules('alchemist')
        self.app = Flask('alchemist')

    def test_unbound(self):
        from alchemist import db

        assert not db.session

    def test_acquire_no_database(self):
        from alchemist import db, exceptions

        with raises(exceptions.ImproperlyConfigured), self.app.app_context():
            assert db.session

    def test_acquire_default(self):
        from alchemist import db

        config = {'default': 'sqlite:///:memory:'}
        with settings(self.app, DATABASES=config), self.app.app_context():
            assert db.session

    def test_repr(self):
        from alchemist import db

        config = {'default': 'sqlite:///:memory:'}
        with settings(self.app, DATABASES=config), self.app.app_context():
            text = '<Session(bind=%r)>' % db.engine['default']
            assert repr(db.session) == text


class TestModel:

    def setup(self):
        utils.unload_modules('alchemist')

        self.app = Flask('alchemist.tests.a')
        self.context = self.app.app_context()
        self.context.push()

        alchemist.configure(self.app)

    def teardown(self):
        self.context.pop()

    def test_metadata(self):
        from alchemist import db

        assert 'alchemist_tests_a_entity' in db.metadata.tables
        assert 'alchemist_tests_a_box' in db.metadata.tables
        assert 'alchemist_tests_a_b_box' in db.metadata.tables
        assert 'alchemist_tests_a_b_plane' in db.metadata.tables

    def test_registry(self):
        from alchemist import db

        assert 'Entity' in db.registry['alchemist.tests.a']
        assert 'Box' in db.registry['alchemist.tests.a']
        assert 'Box' in db.registry['alchemist.tests.a.b']
        assert 'Plane' in db.registry['alchemist.tests.a.b']


class TestQuery:

    def setup(self):
        utils.unload_modules('alchemist')

        self.app = Flask('alchemist.tests.a')
        self.context = self.app.app_context()
        self.context.push()

        alchemist.configure(self.app)

    def teardown(self):
        self.context.pop()

    def test_query(self):
        from alchemist import db
        from .a.models import Entity

        assert isinstance(db.session.query(Entity), db.Query)
        assert isinstance(Entity.query, db.Query)
