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

        super(Manager, self).__init__(app, **kwargs)

        # Discover commands using the flask-components utility.
        for component in components.find('commands', app):
            for command in component.values():
                if (command and isinstance(command, type) and
                        issubclass(command, (script.Command, script.Manager))):
                    self.add_command(command)

    def __call__(self, app=None, **kwargs):
        # Just ignore these features of flask-script as we wrap it and return
        # our configured application.
        return app or self.app

    def run(self, commands=None, default_command=None, context=None):
        """
            Context: A dict of namespaces as the key, and their objects as the
            value. Used to easily inject code into the shell's runtime env.
        """

        if commands:
            self._commands.update(commands)

            # HACK: Overriding the old shell isn't cool.
            # Should do it by default.
        from alchemist.commands import Shell
        self._commands['shell'] = Shell(context=context)

        if default_command is not None and len(sys.argv) == 1:
            sys.argv.append(default_command)

        try:
            result = self.handle(sys.argv[0], sys.argv[1:])
        except SystemExit as e:
            result = e.code

        sys.exit(result or 0)

# Monkey path flask-script (until it can better handle normal WSGI
# applications)
script.Manager.__call__ = Manager.__call__
