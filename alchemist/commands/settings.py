# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext import script
import sys
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer
import pygments
import pprint


class Settings(script.Command):
    """Show the collected configuration settings.
    """

    name = 'settings'

    def __call__(self, app, **kwargs):

        text = pprint.pformat(dict(app.config))

        if sys.stdout.isatty():  # pragma: nocoverage
            text = pygments.highlight(
                text, PythonLexer(), TerminalFormatter())

        print(text)
