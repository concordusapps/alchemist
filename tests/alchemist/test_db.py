# -*- coding: utf-8 -*-
from alchemist.test import settings
from alchemist import db
from alchemist.exceptions import ImproperlyConfigured
from flask import Flask
import contextlib
from pytest import raises


class TestEngine:

    @staticmethod
    def _clear_cache():
        from alchemist.db._engine import Engine
        Engine.__getitem__._cache.clear()

    def setup(self):
        self._clear_cache()
        self.app = Flask('alchemist')
        self.context = self.app.app_context()
        self.context.push()

    def teardown(self):
        self.context.pop()
        self._clear_cache()

    def test_default(self):
        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'default': uri}):

            assert db.engine.url.drivername == 'sqlite'
            assert db.engine.url.database == ':memory:'

    def test_alternative(self):
        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'other': uri}):

            assert db.engine['other'].url.drivername == 'sqlite'
            assert db.engine['other'].url.database == ':memory:'

    def test_missing(self):
        with settings(self.app):

            with raises(ImproperlyConfigured):
                db.engine['default']

    def test_missing_database(self):
        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'other': uri}):

            with raises(ImproperlyConfigured):
                db.engine['default']

    def test_usage(self):
        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'default': uri}):

            with contextlib.closing(db.engine.connect()) as connection:

                result = connection.execute("BEGIN")
                assert result.closed

    def test_lookup(self):
        uri = 'sqlite:///:memory:'
        with settings(self.app, DATABASES={'default': uri}):

            assert 'connect' in dir(db.engine)

    def test_expanded(self):
        config = {
            'engine': 'sqlite',
            'name': 'name',
        }

        with settings(self.app, DATABASES={'default': config}):

            assert db.engine.url.drivername == 'sqlite'
