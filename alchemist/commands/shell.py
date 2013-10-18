# -*- coding: utf-8 -*-
from flask.ext import script
import sys


class Shell(script.Shell):
    """
    Runs a Python shell inside an application context with all
    models pre-loaded.
    """

    name = 'shell'

    def __init__(self, *args, **kwargs):
        # # Default the context maker.
        # kwargs.setdefault('make_context', _make_context)

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
            exec(text, None, None) # _make_context(quiet=True))
            return

        # Fallback to normal cycle.
        super(Shell, self).run(*args, **kwargs)
