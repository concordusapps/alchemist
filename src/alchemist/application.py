# -*- coding: utf-8 -*-
import flask
import sys
import types
import os
from collections import Mapping
import sqlalchemy as sa
from importlib import import_module


def Package(name, application):

    # Import the module.
    module = import_module(name)

    # Wrap the module
    class Inner(type(module)):

        __path__ = module.__path__

        __name__ = module.__name__

        __package__ = module.__package__

        @property
        def application(self):
            application.configure()
            return application

    # Return the module.
    return Inner(name)


class Alchemist(flask.Flask):

    def __init__(self, package_name):
        # Initialize the flask application context.
        super().__init__(package_name)

        # Replace the package with a container module that contains
        # a property reference to the application.
        sys.modules[package_name] = Package(package_name, self)

        #! List of late-bound mounts.
        self._mounts = []

    def _apply_site_configuration(self):
        # Gather configuration from the following places (with precedence):
        #   1 - $<package.application.name>_SETTINGS_MODULE
        #   2 - $ALCHEMIST_SETTINGS_MODULE
        #   3 - <package>.settings

        try:
            # Attempt to get configuration from the application settings.
            self.config.from_object('{}.settings'.format(self.name))

        except ImportError:
            # No settings module or package.
            pass

        # Attempt to get configuration from the environment variables
        env = '{}_SETTINGS_MODULE'.format(self.name.upper()).replace('.', '_')
        for var in ('ALCHEMIST_SETTINGS_MODULE', env):
            if var in os.environ:
                self.config.from_envvar(var)

        # Detect if we are being invoked by a test runner.
        self.config['TESTING'] = False
        for arg in sys.argv:
            if 'test' in arg:
                self.config['TESTING'] = True
                break

        # Alter configuration if we are being invoked by a test runner.
        if self.config['TESTING']:
            # Ensure we use an in-memory sqlite3 database for transactions
            # to increase speed of testing.
            if 'DATABASES' in self.config:
                for name in self.config['DATABASES']:
                    if isinstance(self.config['DATABASES'][name], Mapping):
                        self.config['DATABASES'][name]['engine'] = 'sqlite'
                        self.config['DATABASES'][name]['name'] = ':memory:'

    def configure(self):
        # Configure the application context.
        # Apply the initial site configuration.
        self._apply_site_configuration()

        with self.app_context():
            # After the initial configuration is gathered; each registered
            # package is searched for a settings module or package and that
            # is loaded then the site configuration is re-applied (to
            # keep precedence).
            for package in self.config.get('PACKAGES', ()):
                try:
                    # Attempt to get configuration from the settings module.
                    self.config.from_object('{}.settings'.format(package))

                except ImportError:
                    # No settings module in package.
                    pass

                try:
                    # Attempt to import the model module or package.
                    import_module('{}.models'.format(package))

                except ImportError:
                    # No component in package.
                    pass

                # Re-apply the initial site configuration.
                self._apply_site_configuration()

        # Process database configuration.
        # Expand each reference into a database engine.
        # TODO: Support PORT, HOST, USERNAME, and PASSWORD
        for name in self.config.get('DATABASES', ()):
            db = self.config['DATABASES'][name]
            if isinstance(db, Mapping):
                uri = '{}:///{}'.format(db['engine'], db['name'])
                echo = db.get('echo', False)
                engine = sa.create_engine(uri, echo=echo)
                self.config['DATABASES'][name] = engine

        # Iterate through the delayed mounts and run each handlers.
        for handler in self._mounts:
            handler()

    def mount(self, name):
        """Import the package after configuration.

        Calls to `mount` are late-bound and don't actually happen until
        after `configure` is called.
        """
        # Create a closure and bind the mount function.
        def _handle():
            with self.app_context():
                import_module(name)

        # Add it to the handlers to run.
        self._mounts.append(_handle)
