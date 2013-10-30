# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from . import utils
from flask.ext import components
from importlib import import_module
import flask
import inspect
import os


def configure(self, app):

    # Gather configuration from the following places:
    #  1. alchemist.conf.default_settings
    app.config.from_object('alchemist.conf.default_settings')

    #  2. <package>.settings

    try:
        app.config.from_object('%s.settings' % app.name)

    except ImportError:
        pass

    #  3. $ALCHEMIST_SETTINGS_MODULE

    app.config.from_envvar('ALCHEMIST_SETTINGS_MODULE', silent=True)

    #  4. $<package>_SETTINGS_MODULE

    var = '%s_SETTINGS_MODULE' % app.name.replace('.', '_').upper()
    app.config.from_envvar(var, silent=True)

    # Gather configuration from each registered component.

    name = app.name
    for component in components.find('settings', app, raw=True):
        if component.__package__ != name or component.__name__ != name:
            app.config.from_object(component)

    # Resolve deferred configuration.

    from alchemist.conf import defer

    with app.app_context():
        for name, value in app.config.items():
            if isinstance(value, defer):
                app.config[name] = value.resolve()

    # Gather and import all models modules or packages of the
    # registered components.

    components.find('models', app, raw=True)


@utils.memoize
def _get_application_from_name(self, name):

    # Take the passed name (eg. 'sandbox') and check the following
    # locations for a flask application:
    #   <name>.app
    #   <name>.application
    #   <name>.app.application
    #   <name>.app.app

    for part in ('', '.app'):
        try:
            module = import_module(name + part)

        except ImportError:
            return None

        app = getattr(module, 'app', None)
        if app and isinstance(app, flask.Flask):
            return app

        app = getattr(module, 'application', None)
        if app and isinstance(app, flask.Flask):
            return app


@utils.memoize
def _find_application(self):

    # Check for an environment variable declaring where the central
    # application lives.

    name = os.environ.get('ALCHEMIST_APPLICATION')
    if name:
        app = self._get_application_from_name(name)
        if app:
            return app

    # Inspect the stack to find the application.
    # This is intended for ease during development and for production
    # to lock-in the application via the environment variable.

    for frame in inspect.stack()[1:]:
        name = frame[0].f_globals.get('__package__')
        if name and name != 'alchemist':
            app = self._get_application_from_name(name)
            if app:
                return app


@property
def application(self):

    # Short-circuit this if we're in an application context.

    if flask.current_app:
        return flask.current_app

    # Attempt to find the application.

    return self._find_application()


utils.make_module_class(__name__)
