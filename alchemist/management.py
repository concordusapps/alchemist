# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext import script, components
import colorama
import sys


class Manager(script.Manager):

    def __init__(self, app, **kwargs):

        # Initialize color output.
        if sys.stdout.isatty():  # pragma: nocoverage
            colorama.init()

        # Disable loading of default flask-script commands.
        kwargs.setdefault('with_default_commands', False)

        super(Manager, self).__init__(lambda: app, **kwargs)

        # Discover commands using the flask-components utility.
        for component in components.find('commands', app):
            for command in component.values():
                if (command and isinstance(command, type) and
                        issubclass(command, (script.Command, script.Manager))):
                    self.add_command(command)

    def __call__(self, app=None, **kwargs):
        # Just ignore these features of flask-script as we wrap it and return
        # our configured application.
        # import ipdb; ipdb.set_trace()
        # from alchemist.app import application

        return self.app
