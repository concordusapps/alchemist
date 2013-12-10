# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from . import utils
from flask.ext import components
from importlib import import_module
import flask
import inspect
import os
import sys
import sqlalchemy as sa
from sqlalchemy_utils import coercion_listener


def configure(self, app):

    # Detect if we are being invoked by a test runner.
    # Checks the first and second arguments to determine if we are being
    # run by a test runner.
    # Able to match `py.test`, `nosetests`, `alchemist test`,
    # and `python setup.py test`.

    app.config['TESTING'] = False
    count = 3 if os.path.basename(sys.argv[0]).startswith('python') else 2
    for argument in sys.argv[0:count]:
        if 'test' in argument:
            # We are, in fact, being run by a test runner.
            app.config['TESTING'] = True
            break

    # Gather configuration from the following places:
    #  1. alchemist.conf.default_settings
    app.config.from_object('alchemist.conf.default_settings')

    #  2. <package>.settings

    try:
        app.config.from_object('%s.settings' % app.name)

    except ImportError:
        pass

    #  3. Gather configuration from each registered component.

    name = app.name
    for component in components.find('settings', app, raw=True):
        if component.__package__ != name or component.__name__ != name:
            app.config.from_object(component)

    #  4. $ALCHEMIST_SETTINGS_MODULE

    app.config.from_envvar('ALCHEMIST_SETTINGS_MODULE', silent=True)

    #  5. $<package>_SETTINGS_MODULE

    var = '%s_SETTINGS_MODULE' % app.name.replace('.', '_').upper()
    app.config.from_envvar(var, silent=True)

    # Resolve deferred configuration.

    from alchemist.conf import defer

    with app.app_context():
        for name, value in app.config.items():
            if isinstance(value, defer):
                app.config[name] = value.resolve()

    # Gather and import all models modules or packages of the
    # registered components.

    components.find('models', app, raw=True)

    # Register the coercion listener.
    sa.event.listen(sa.orm.mapper, 'mapper_configured', coercion_listener)


@utils.memoize
def _get_application_from_name(self, name):

    # Take the passed name (eg. 'sandbox') and check the following
    # locations for a flask application:
    #   <name>.app
    #   <name>.application
    #   <name>.app.application
    #   <name>.app.app

    if not name:
        return None

    for part in ('', '.app'):
        try:
            module = import_module(name + part)

        except ImportError:
            continue

        app = getattr(module, 'app', None)
        if app and isinstance(app, flask.Flask):
            return app

        app = getattr(module, 'application', None)
        if app and isinstance(app, flask.Flask):
            return app

    return self._get_application_from_name('.'.join(name.split('.')[:-1]))


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

    for frame in reversed(inspect.stack()[1:]):
        name = frame[0].f_globals.get('__package__')
        if (name and (not name.startswith('alchemist')
                      or name.startswith('alchemist.tests.a'))):
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
