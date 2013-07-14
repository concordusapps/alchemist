# -*- coding: utf-8 -*-
import sys
from flask.ext import script
from termcolor import colored
from alchemist import application, db


def _make_context(quiet=False):
    # Start by adding the session instance to the namespace.
    namespace = {'db': db, 'session': db.session}

    if not quiet:
        # Let the user know.
        print(colored('from alchemist import db', 'green'))
        print(colored('session = db.session', 'green'))

    # Iterate through all models and add those to the namespace.
    module = {}
    for name, models in application.models.items():
        for model in models:
            if model.__module__ not in module:
                module[model.__module__] = []

            module[model.__module__].append(model.__name__)
            namespace[model.__name__] = model

    if not quiet:
        # Let the user know.
        for name, models in module.items():
            items = ', '.join(models)
            print(colored('from %s import %s' % (name, items), 'green'))

    # Return the constructed namespace.
    return namespace


class Shell(script.Shell):
    """
    Runs a Python shell inside an application context with all
    models pre-loaded.
    """

    def __init__(self, *args, **kwargs):
        # Default the context maker.
        kwargs.setdefault('make_context', _make_context)

        # Continue initialization.
        super().__init__(*args, **kwargs)

    def get_options(self):
        options = super().get_options()

        # Add an additional option that allows for piping of input
        # to the shell.
        options += script.Option('--pipe', action="store_true", dest='pipe'),

        return options

    def run(self, pipe, *args, **kwargs):
        if pipe:
            # User is attempting to pipe in script through stdin.
            text = sys.stdin.read()
            exec(text, None, _make_context(quiet=True))
            return

        # Fallback to normal cycle.
        super().run(*args, **kwargs)
