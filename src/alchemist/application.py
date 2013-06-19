# -*- coding: utf-8 -*-
import flask
import os
from importlib import import_module

def Application(package):
    # Instantiate the flask application context.
    context = flask.Flask(package)

    # Configure the application.
    # Pull configuration from the project settings module.
    context.config.from_object('{}.settings'.format(package))

    # Pull configuration from the package settings' modules.
    for name in context.config.get('PACKAGES', []):
        context.config.from_object('{}.settings'.format(name))

    # Pull configuration from the project-specific settings module.
    module = '{}_SETTINGS_MODULE'.format(package).replace('.', '_')
    if module in os.environ:
        context.config.from_envvar(module)

    # Pull configuration from the a generic settings module.
    if 'SETTINGS_MODULE' in os.environ:
        context.config.from_envvar('SETTINGS_MODULE')

    # Register packages.
    for name in context.config.get('PACKAGES', []):
        with context.app_context():
            import_module('{}.models'.format(name))
            import_module('{}.api'.format(name))

    # Return the flask context.
    return context
