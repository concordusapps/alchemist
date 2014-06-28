# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from alchemist import utils, exceptions
from alchemist.conf import settings
import sqlalchemy as sa
import six
import threading
from sqlalchemy.engine.url import URL, make_url


class Engine(object):

    def __getattribute__(self, name):
        return getattr(self['default'], name)

    def __dir__(self):
        return dir(self['default'])

    def __repr__(self):
        return repr(self['default'])

    @utils.memoize
    def __getitem__(self, name):

        if 'DATABASES' not in settings:
            raise exceptions.ImproperlyConfigured(
                'DATABASES not configured in project settings.')

        if name not in settings['DATABASES']:
            raise exceptions.ImproperlyConfigured(
                '%r not present in DATABASES configuration.' % name)

        config = settings['DATABASES'][name]

        if isinstance(config, six.string_types):
            url = make_url(config)
            options = {}

        else:
            config = dict(map(lambda i: (i[0].lower(), i[1]), config.items()))
            options = config.get('options', {})
            url = URL(
                config['engine'],
                username=config.get('username', config.get('user')),
                password=config.get('password', config.get('pass')),
                host=config.get('hostname', config.get('host')),
                port=config.get('port'),
                database=config.get('name', config.get('database')))

        # If alchemist is invoked by a test runner we should switch to using
        # testing databases.

        if settings['TESTING']:

            if url.drivername.startswith('sqlite'):

                # Switch to using an in-memory database for sqlite.
                url.database = ':memory:'

            else:

                # Switch to using a named testing database for other dialects.
                ident = threading.current_thread().ident
                url.database = 'test_%s_%s' % (url.database, ident)

        # Apply MySQL hacks to make MySQL play nice.
        pool_size = None
        pool_recycle = None
        if url.drivername.startswith('mysql'):
            pool_size = 10
            pool_recycle = 7200

        # Get "global" options for the database engine.
        pool_size = settings.get('DATABASE_POOL_SIZE', pool_size)
        if pool_size:
            options.setdefault('pool_size', pool_size)

        pool_recycle = settings.get('DATABASE_POOL_RECYCLE', pool_recycle)
        if pool_recycle:
            options.setdefault('pool_recycle', pool_recycle)

        pool_timeout = settings.get('DATABASE_POOL_TIMEOUT')
        if pool_timeout:
            options.setdefault('pool_timeout', pool_timeout)

        # Forward configuration to sqlalchemy and create the engine.
        engine = sa.create_engine(url, **options)

        if settings["DEBUG"]:
            # Create a no-op listener if we're in debug mode.
            from sqlalchemy.event import listen
            listen(engine, "after_cursor_execute", lambda *a, **kw: None)

        # Return the created engine.
        return engine


def clear_cache():
    Engine.__getitem__._cache.clear()


engine = Engine()
