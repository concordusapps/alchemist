# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
import alchemist
import contextlib
import py
from alchemist.test import settings
from flask import Flask
from pytest import raises
from sqlalchemy.engine.result import ResultProxy
from sqlalchemy.exc import OperationalError
from . import utils


try:   # pragma: nocoverage
    from unittest import mock

except ImportError:  # pragma: nocoverage
    import mock


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
                assert isinstance(result, ResultProxy)

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


class TestInitializeOperation:

    def setup(self):
        self.app = Flask('alchemist.tests.a')
        self.context = self.app.app_context()
        self.context.push()

        alchemist.configure(self.app)

    def teardown(self):
        from alchemist import db
        db.clear()

        self.context.pop()

    def test_init(self):
        from alchemist import db
        from .a.models import Entity

        with raises(OperationalError):
            assert Entity.query.all()

        db.init()

        assert Entity.query.all() == []

    def test_init_component(self):
        from alchemist import db
        from .a.models import Entity

        with raises(OperationalError):
            assert Entity.query.all()

        db.init(names=['alchemist.tests.a'])

        assert Entity.query.all() == []

    def test_init_full_name(self):
        from alchemist import db
        from .a.models import Entity

        with raises(OperationalError):
            assert Entity.query.all()

        db.init(names=['alchemist.tests.a.models.Entity'])

        assert Entity.query.all() == []

    def test_init_short_name(self):
        from alchemist import db
        from .a.models import Entity

        with raises(OperationalError):
            assert Entity.query.all()

        db.init(names=['alchemist.tests.a:Entity'])

        assert Entity.query.all() == []

    def test_init_twice(self):
        from alchemist import db
        from .a.models import Entity

        with raises(OperationalError):
            assert Entity.query.all()

        db.init(names=['alchemist.tests.a:Entity'])

        assert Entity.query.all() == []

        db.init(names=['alchemist.tests.a:Entity'])

        assert Entity.query.all() == []

    def test_init_verbose(self):
        from alchemist import db

        capture = py.io.StdCapture(out=True, in_=False)
        db.init(verbose=True)
        out, err = capture.done()

        text = err.read()

        assert 'create' in text
        assert 'alchemist_tests_a_entity' in text

    def test_init_offline(self):
        from alchemist import db
        from .a.models import Entity

        with raises(OperationalError):
            assert Entity.query.all()

        capture = py.io.StdCapture(out=True, in_=False)
        db.init(offline=True)
        _, _ = capture.done()

        with raises(OperationalError):
            assert Entity.query.all()

    def test_init_echo(self):
        from alchemist import db

        capture = py.io.StdCapture(out=True, in_=False)
        db.init(echo=True)
        out, err = capture.done()

        text = out.read()

        assert 'CREATE TABLE' in text
        assert 'alchemist_tests_a_entity' in text


class TestClearOperation:

    def setup(self):
        from alchemist import db

        self.app = Flask('alchemist.tests.a')
        self.context = self.app.app_context()
        self.context.push()

        db.init()

    def teardown(self):
        from alchemist import db

        db.clear()

        self.context.pop()

    def test_clear(self):
        from alchemist import db
        from .a.models import Entity

        assert Entity.query.all() == []

        db.clear()

        with raises(OperationalError):
            assert Entity.query.all()

    def test_clear_name(self):
        from alchemist import db
        from .a.models import Entity

        assert Entity.query.all() == []

        db.clear(names=['alchemist.tests.a'])

        with raises(OperationalError):
            assert Entity.query.all()

    def test_clear_twice(self):
        from alchemist import db
        from .a.models import Entity

        assert Entity.query.all() == []

        db.clear()

        with raises(OperationalError):
            assert Entity.query.all()

        db.clear()

        with raises(OperationalError):
            assert Entity.query.all()

    def test_clear_verbose(self):
        from alchemist import db

        capture = py.io.StdCapture(out=True, in_=False)
        db.clear(verbose=True)
        out, err = capture.done()

        text = err.read()

        assert 'drop' in text
        assert 'alchemist_tests_a_entity' in text

    def test_clear_offline(self):
        from alchemist import db
        from .a.models import Entity

        assert Entity.query.all() == []

        capture = py.io.StdCapture(out=True, in_=False)
        db.clear(offline=True)
        _, _ = capture.done()

        assert Entity.query.all() == []

    def test_clear_echo(self):
        from alchemist import db

        capture = py.io.StdCapture(out=True, in_=False)
        db.clear(echo=True)
        out, err = capture.done()

        text = out.read()

        assert 'DROP TABLE' in text
        assert 'alchemist_tests_a_entity' in text


class TestFlushOperation:

    def setup(self):
        from alchemist import db

        self.app = Flask('alchemist.tests.a')
        self.context = self.app.app_context()
        self.context.push()

        db.init()

        from .a.models import Entity

        db.session.add(Entity())
        db.session.commit()

    def teardown(self):
        from alchemist import db

        db.clear()

        self.context.pop()

    def test_flush(self):
        from alchemist import db
        from .a.models import Entity

        assert len(Entity.query.all()) == 1

        db.flush()

        assert Entity.query.all() == []

    def test_flush_non_existing(self):
        from alchemist import db
        from .a.models import Entity

        assert len(Entity.query.all()) == 1

        db.clear()
        db.flush()

        with raises(OperationalError):
            assert Entity.query.all()

    def test_flush_name(self):
        from alchemist import db
        from .a.models import Entity

        assert len(Entity.query.all()) == 1

        db.flush(names=['alchemist.tests.a'])

        assert Entity.query.all() == []

    def test_flush_twice(self):
        from alchemist import db
        from .a.models import Entity

        assert len(Entity.query.all()) == 1

        db.flush()

        assert Entity.query.all() == []

        db.flush()

        assert Entity.query.all() == []

    def test_flush_verbose(self):
        from alchemist import db

        capture = py.io.StdCapture(out=True, in_=False)
        db.flush(verbose=True)
        out, err = capture.done()

        text = err.read()

        assert 'flush' in text
        assert 'alchemist_tests_a_entity' in text

    def test_flush_offline(self):
        from alchemist import db
        from .a.models import Entity

        assert len(Entity.query.all()) == 1

        capture = py.io.StdCapture(out=True, in_=False)
        db.flush(offline=True)
        _, _ = capture.done()

        assert len(Entity.query.all()) == 1

    def test_flush_echo(self):
        from alchemist import db

        capture = py.io.StdCapture(out=True, in_=False)
        db.flush(echo=True)
        out, err = capture.done()

        text = out.read()

        assert 'DELETE FROM' in text
        assert 'alchemist_tests_a_entity' in text


class TestShellOperation:

    @staticmethod
    def _clear_cache():
        from alchemist.db._engine import Engine
        Engine.__getitem__._cache.clear()

    def setup(self):
        self._clear_cache()
        self.app = Flask('alchemist.tests.a')
        self.context = self.app.app_context()
        self.context.push()

    def teardown(self):
        self.context.pop()
        self._clear_cache()

    def test_shell_sqlite3(self):
        from alchemist import db

        with settings(self.app, DATABASES={'default': 'sqlite:///:memory:'}):

            target = mock.MagicMock()
            with mock.patch('os.execvp', target):
                db.shell()

            target.assert_called_with('sqlite3', ['sqlite3', ':memory:'])

    def test_shell_mysql(self):
        from alchemist import db

        uri = 'mysql+oursql://user:pass@host:55/name'
        with settings(self.app, DATABASES={'default': uri}):

            target = mock.MagicMock()
            with mock.patch('os.execvp', target):
                db.shell()

            target.assert_called_with('mysql', [
                'mysql', '--user=user', '--password=pass',
                '--host=host', '--port=55', 'name'])

    def test_shell_mysql_socket(self):
        from alchemist import db

        uri = ('mysql+oursql://user:pass@localhost/name?'
               'unix_socket=/some/file/over/there.socket')
        with settings(self.app, DATABASES={'default': uri}):

            target = mock.MagicMock()
            with mock.patch('os.execvp', target):
                db.shell()

            target.assert_called_with('mysql', [
                'mysql', '--user=user', '--password=pass',
                '--socket=/some/file/over/there.socket', 'name'])
