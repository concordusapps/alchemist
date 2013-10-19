# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext import script
from alchemist import db
from termcolor import colored
from collections import defaultdict
import sys


def _iter_context():
    for component, registry in db.registry.items():
        for name, model in registry.items():
            if not name.startswith('_'):
                yield name, model


def _make_context():
    """Create the namespace of items already pre-imported when using shell
    """
    namespace = {'db': db, 'session': db.session}
    namespace.update(_iter_context())
    return namespace


class Shell(script.Shell):
    """
    Runs a Python shell inside an application context with all
    models pre-loaded.
    """

    name = 'shell'

    @property
    def banner(self):
        text = colored('from alchemist import db\n', 'green')
        text += colored('session = db.session\n', 'green')

        modules = defaultdict(set)
        for name, model in _iter_context():
            modules[model.__module__].add(name)

        for module, name in modules.items():
            context = (module, ', '.join(name))
            text += colored('from %s import %s\n' % context, 'green')

        return text

    @banner.setter
    def banner(self, value):
        """Flask script attempts to set the banner to itself for some unknown
        reason.  So just don't bother."""
        pass

    def __init__(self, *args, **kwargs):
        # # Default the context maker.
        kwargs.setdefault('make_context', _make_context)
        kwargs.setdefault('banner')

        # Continue initialization.
        super(Shell, self).__init__(*args, **kwargs)

    def get_options(self):
        options = super(Shell, self).get_options()

        # Add an additional option that allows for piping of input
        # to the shell.
        options += script.Option('--pipe', action="store_true"),

        return options

    def run(self, pipe, *args, **kwargs):
        if pipe:
            # User is attempting to pipe in script through stdin.
            text = sys.stdin.read()
            exec(text, None, _make_context())
            return

        # Fallback to normal cycle.
        super(Shell, self).run(*args, **kwargs)
