# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from alchemist import utils, exceptions
from alchemist.conf import settings
import sqlalchemy as sa
import six
from sqlalchemy.engine.url import URL


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
            url = config
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

        return sa.create_engine(url, **options)


engine = Engine()
