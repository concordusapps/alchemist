# -*- coding: utf-8 -*-
import flask
from itertools import chain
import sys
import types
import os
import io
import ipaddress
from collections import Mapping, OrderedDict
import sqlalchemy as sa
from sqlalchemy.ext.declarative import DeclarativeMeta
from importlib import import_module
from flask import current_app as application
from .meta import version as __version__

__all__ = [
    'Alchemist',
    'application',
]


def wrap_module(name, application):

    # Wrap the module with a nested module that
    # contains property accessors for late-bound configuration.
    class Module(types.ModuleType):

        @property
        def application(self):
            application.configure()
            return application

    # Update the inner module with the actual contents.
    instance = Module(__name__)
    instance.__dict__.update(sys.modules[name].__dict__)

    # Return the wrapped module.
    return instance


class Alchemist(flask.Flask):

    @staticmethod
    def _build_database_uri(testing=False, **kwargs):
        # Resolve the expanded form into a database URI.
        o = io.StringIO()

        # Build key names and get properly.
        def key(name):
            if testing and ('test_' + name) in kwargs:
                return 'test_' + name

            return name

        # Add the designated engine.
        o.write(kwargs[key('engine')])
        o.write(':///')

        # Add the username.
        user = False
        if key('user') in kwargs:
            o.write(kwargs[key('user')])
            user = True

        elif key('username') in kwargs:
            o.write(kwargs[key('username')])
            user = True

        # Add the password.
        if user:
            if key('pass') in kwargs:
                o.write(':')
                o.write(kwargs[key('pass')])

            elif key('password') in kwargs:
                o.write(':')
                o.write(kwargs[key('password')])

        # Add the hostname.
        null = 'localhost' if user else None
        hostname = kwargs.get(key('host'), kwargs.get(key('hostname'), null))
        if hostname:
            if user:
                # Write the user / host separator.
                o.write('@')

            ipaddr = True
            try:
                # Check if this is an ip address.
                ipaddress.ip_address(hostname)
                o.write('[')

            except ValueError:
                # This is not.
                ipaddr = False

            # Write out the hostname.
            o.write(hostname)
            if ipaddr:
                o.write(']')

        # Add the port.
        if key('port') in kwargs:
            o.write(':')
            o.write(str(kwargs[key('port')]))

        # Add the name.
        if hostname:
            o.write('/')

        # Default a testing name if we have one.
        name = None
        if testing and 'test_name' not in kwargs:
            if kwargs[key('engine')] == 'sqlite':
                name = ':memory:'

            else:
                name = 'test_' + kwargs['name']

        if name is None:
            name = kwargs[key('name')]

        o.write(name)

        # Return our constructed URI.
        return o.getvalue()

    def __init__(self, name, *args, **kwargs):
        # Initialize the flask application context.
        super().__init__(name, *args, **kwargs)

        # Replace the package with a container module that contains
        # a property reference to the application.
        sys.modules[name] = wrap_module(name, self)

        #! Collections of database models and metadata.
        self.models = OrderedDict()
        self.metadata = OrderedDict()

    def _apply_site_configuration(self):
        # Gather configuration from the following places (with precedence):
        #   1. $<package.application.name>_SETTINGS_MODULE
        #   2. $ALCHEMIST_SETTINGS_MODULE
        #   3. <project>.settings

        # Set default settings.
        # The default packages array contains just the alchemist lib which
        # includes all default commands.
        self.config['PACKAGES'] = ['alchemist']

        # The default server configuration enables threading.
        self.config['SERVER'] = {
            'host': 'localhost',
            'port': 8000,
            'threading': True
        }

        try:
            # Attempt to get configuration from the project settings.
            self.config.from_object('{}.settings'.format(self.name))

        except ImportError:
            # No settings module or package.
            pass

        # Attempt to get configuration from the environment variables.
        for name in ['ALCHEMIST', self.name.upper().replace('.', '_')]:
            var = '%s_SETTINGS_MODULE' % name
            if var in os.environ:
                self.config.from_envvar(var)

    def configure(self):
        """Collect settings and configure the application instance."""

        # Establish an application context.
        context = self.app_context()
        context.push()

        # Detect if we are being invoked by a test runner.
        # Checks the first and second arguments to determine if we are being
        # run by a test runner.
        # Able to match `py.test`, `nosetests`, `alchemist test`,
        # and `python setup.py test`.
        self.config['TESTING'] = False
        count = 3 if os.path.basename(sys.argv[0]).startswith('python') else 2
        for argument in sys.argv[0:count]:
            if 'test' in argument:
                # We are, in fact, being run by a test runner.
                self.testing = self.config['TESTING'] = True
                break

        # Apply the initial site configuration.
        self._apply_site_configuration()

        # After the initial configuration is gathered; each registered
        # package is searched for a settings module or package and that
        # is loaded then the site configuration is re-applied (to
        # keep precedence and allow dynamic behavior).
        all_models = set()
        for name in chain(self.config.get('PACKAGES', ()), (self.name,)):
            try:
                # Attempt to get configuration from the settings module.
                self.config.from_object('{}.settings'.format(name))

            except ImportError:
                # No settings module.
                pass

            try:
                # Attempt to import a models module or name.
                models = import_module('{}.models'.format(name))

            except ImportError:
                # No models module found.
                models = None

            # Import the name itself.
            package = import_module(name)

            # Initialize models set.
            self.models[name] = set()

            # Create filterer that only grabs instances of DeclarativeMeta.
            restrict = lambda o: set(filter(
                lambda x: isinstance(x, DeclarativeMeta),
                o._decl_class_registry.values()))

            # Try searching through the namespaces of both the package
            # and the models module to find the metadata.
            for module in package, models:
                if module:
                    for cls in vars(module).values():
                        if isinstance(cls, type) and cls not in all_models:
                            meta = getattr(cls, 'metadata', None)
                            if meta and isinstance(meta, sa.MetaData):
                                # Found a match; move along.
                                self.metadata[name] = meta

                                # Update registry.
                                self.models[name].update(restrict(cls))
                                all_models.add(cls)

                                # Clear modules.
                                modules, package = None, None
                                break

            # Re-apply the site configuration.
            self._apply_site_configuration()

        # Release the application context.
        context.pop()

        # Process and resolve database configuration.
        self.databases = {}
        for name, db in self.config.get('DATABASES', {}).items():
            if isinstance(db, Mapping):
                # Build the database URI.
                uri = self._build_database_uri(testing=self.testing, **db)
                echo = db.get('echo', False)

            else:
                # The database object should be the URI.
                uri = db
                echo = False

            # Create the database engine.
            self.databases[name] = sa.create_engine(uri, echo=echo)
