# -*- coding: utf-8 -*-
import flask
import os
import sys
import re
import sqlalchemy as sa
from sqlalchemy import orm
from importlib import import_module


def _apply_site_configuration(application):
    # Configure the application.
    # Pull configuration from the project settings module.
    application.config.from_object('{}.settings'.format(application.name))

    # Pull configuration from the project-specific settings module.
    module = '{}_SETTINGS_MODULE'.format(application.name).replace('.', '_')
    if module in os.environ:
        application.config.from_envvar(module)

    # Pull configuration from the a generic settings module.
    if 'SETTINGS_MODULE' in os.environ:
        application.config.from_envvar('SETTINGS_MODULE')

    # Detect if were testing.
    testing = False
    for arg in sys.argv:
        if 'test' in arg:
            testing = True
            break

    if testing:
        # Change configuration if we're testing.
        application.config['DATABASE_URI'] = 'sqlite:///:memory:'
        application.config['DATABASE_ENGINE'] = sa.create_engine(
            application.config['DATABASE_URI'], echo=False)

        application.config['DATABASE_SESSION'].configure(
            bind=application.config['DATABASE_ENGINE'])

    if application.config['DATABASE_URI'].startswith('sqlite:'):
        # If we're running with SQLITE we'd like datbase foreign key support
        # and REGEXP support.
        def _sqlite3_regexp(pattern, text):
            return bool(re.search(pattern, text))

        def _on_connect(connection, record):
            connection.create_function('regexp', 2, _sqlite3_regexp)
            connection.execute('PRAGMA foreign_keys=ON')

        sa.event.listen(application.config['DATABASE_ENGINE'], 'connect',
                        _on_connect)


def Application(package):
    # Instantiate the flask application context.
    context = flask.Flask(package)

    # Apply site configuration.
    _apply_site_configuration(context)
    
    # Return the flask context.
    return context


def _add_package_context(application, package, context):
    with application.app_context():
        try:
            # Attempt to pull in this context.
            import_module('{}.{}'.format(package, context))

        except ImportError:
            # No defined context; skip
            pass


def add_package(application, package, **kwargs):
    # TODO: Packages could be stored as actual objects so they can be
    #   queried as to what was installed?
    # Ensure the PACKAGES configuration is at least an empty array.
    if not application.config.get('PACKAGES'):
        application.config['PACKAGES'] = []

    # Add the package to the PACKAGES configuration.
    application.config['PACKAGES'].append(package)

    try:
        # Apply package configuration.
        application.config.from_object('{}.settings'.format(package))

    except ImportError:
        # No settings module.
        pass

    # Apply site configuration.
    _apply_site_configuration(application)

    # Set argument defaults.
    kwargs.setdefault('models', True)
    kwargs.setdefault('api', True)
    kwargs.setdefault('views', True)

    # Register the package in all requested contexts.
    for context in ('models', 'api', 'views'):
        if kwargs[context]:
            _add_package_context(application, package, context)
