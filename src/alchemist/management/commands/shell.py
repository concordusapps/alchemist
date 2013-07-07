# -*- coding: utf-8 -*-
import collections
import sqlalchemy as sa
from alchemist.conf import settings
from alchemist import db
from flask.ext import script
from termcolor import colored
from importlib import import_module


def _collect_models():
    """
    Iterate through all registered packages and create a dictionary
    mapping package names to base metadata.
    """
    # Enumerate through each installed package.
    all_models = set()
    models = collections.OrderedDict()
    for name in settings.get('PACKAGES', ()):
        try:
            # Attempt to import a models module or package.
            module = import_module('{}.models'.format(name))

        except ImportError:
            # No models module found.
            module = None

        # Import the package.
        package = import_module(name)

        # Initialize models set.
        models[name] = set()

        # Try searching through the namespaces of both the package
        # and the models module to find models.
        for mod in package, module:
            if mod:
                for cls in mod.__dict__.values():
                    meta = getattr(cls, 'metadata', None)
                    if meta and isinstance(meta, sa.MetaData):
                        if cls in models[name] or cls in all_models:
                            # Duplicate; keep looking.
                            continue

                        # Found a match; move along.
                        all_models.add(cls)
                        models[name].add(cls)

        # Did we get anythng; if not, remove it.
        if not models[name]:
            del models[name]

    # Return the collection of metadata.
    return models


class Shell(script.Shell):
    """Runs a Python shell inside Flask application context.
    """

    #! Name of the command as it is invoked on the command line.
    name = 'shell'

    def _make_context(self):
        # Start by adding the session instance to the user's namespace.
        namespace = {'db': db, 'session': db.session}

        print(colored('from alchemist import db', 'green'))
        print(colored('session = db.session', 'green'))

        # Collect all the models and add those to the namespace.
        for name, models in _collect_models().items():
            # Append the models to the namespace.
            namespace.update({m.__name__: m for m in models})

            # Print what we've done.
            items = map(lambda x: x.__name__, models)
            print(colored('from {}.models import {}'.format(
                name, ', '.join(items)), 'green'))

        # Return the context.
        return namespace

    def __init__(self, *args, **kwargs):
        # Default the context maker.
        kwargs.setdefault('make_context', self._make_context)

        # Continue initialization.
        super().__init__(*args, **kwargs)
