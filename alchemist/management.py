# -*- coding: utf-8 -*-
from flask.ext import script, components


class Manager(script.Manager):

    def __init__(self, app, **kwargs):

        # Disable loading of default flask-script commands.
        kwargs.setdefault('with_default_commands', False)

        super(Manager, self).__init__(app, **kwargs)

        # Discover commands using the flask-components utility.
        for component in components.find('commands', app):
            for command in component.values():
                if issubclass(command, (script.Command, script.Manager)):
                    self.add_command(command)
