# -*- coding: utf-8 -*-
from alchemist import utils, exceptions
from alchemist.conf import settings
import sqlalchemy as sa
import six
import socket
from six.moves import cStringIO

try:
    from urllib.parse import urlunsplit

except ImportError:
    from urlparse import urlunsplit


def _is_valid_ipv4_address(text):
    try:
        socket.inet_pton(socket.AF_INET, text)

    except AttributeError:
        try:
            socket.inet_aton(text)

        except socket.error:
            return False

    except socket.error:
        return False

    return True


def _is_valid_ipv6_address(text):
    try:
        socket.inet_pton(socket.AF_INET6, text)

    except socket.error:
        return False

    return True


def _is_ip_address(text):
    return _is_valid_ipv4_address(text) or _is_valid_ipv6_address(text)


def _build_engine_uri(driver, host, port, username, password, name):

    # Build the network location (netloc)

    netloc = cStringIO()

    if username:
        netloc.write(username)

        if password:
            netloc.write(':')
            netloc.write(password)

        netloc.write('@')

    if _is_ip_address(host):
        netloc.write('[')
        netloc.write(host)
        netloc.write(']')

    else:
        netloc.write(host)

    if port:
        netloc.write(':')
        netloc.write(str(port))

    # Construct the remainder of the URI and return it.

    return urlunsplit((driver, netloc.getvalue(), name, '', ''))


class Engine(object):

    def __getattribute__(self, name):
        return getattr(self['default'], name)

    def __dir__(self):
        return dir(self['default'])

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
            url = _build_engine_uri(
                driver=config['engine'],
                username=config.get('username', config.get('user')),
                password=config.get('password', config.get('pass')),
                host=config.get('hostname', config.get('host')),
                port=config.get('port'),
                name=config['name'])

            import ipdb; ipdb.set_trace()

        return sa.create_engine(url, **options)


engine = Engine()
