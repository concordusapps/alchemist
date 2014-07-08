# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
import types
import sys
import six
import functools
from termcolor import colored
from werkzeug.wsgi import DispatcherMiddleware as BaseDispatcherMiddleware
from importlib import import_module


def make_module_class(name):
    """Takes the module referenced by name and make it a full class.
    """

    source = sys.modules[name]

    members = vars(source)
    is_descriptor = lambda x: not isinstance(x, type) and hasattr(x, '__get__')
    descriptors = {k: v for (k, v) in members.items() if is_descriptor(v)}
    members = {k: v for (k, v) in members.items() if k not in descriptors}
    descriptors['__source'] = source

    target = type(name, (types.ModuleType,), descriptors)(name)
    target.__dict__.update(members)

    sys.modules[name] = target


def memoize(obj):
    cache = obj._cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)

        return cache[args]

    return memoizer


def print_(indicator, name, target='', extra=''):
    six.print_(
        colored(' ' + indicator, 'white', attrs=['dark']),
        colored(name, 'cyan'),
        colored(target, 'white'),
        colored(extra, 'white', attrs=['dark']),
        file=sys.stderr)


class DispatcherMiddleware(BaseDispatcherMiddleware):

    def __init__(self, app, mounts):
        # Load each mount (if needed) using import_module
        for route, application in mounts.items():
            if isinstance(application, six.string_types):
                module, name = application.rsplit(".", 1)
                mounts[route] = getattr(import_module(module), name)

        # Continue initialization.
        super().__init__(app, mounts)

    def __getattr__(self, name):
        return getattr(self.app, name)
