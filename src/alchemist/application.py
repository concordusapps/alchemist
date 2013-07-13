# -*- coding: utf-8 -*-
import flask
import sys
import types
import os
import sqlalchemy as sa


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

    def __init__(self, name, *args, **kwargs):
        # Initialize the flask application context.
        super().__init__(name, *args, **kwargs)

        # Replace the package with a container module that contains
        # a property reference to the application.
        sys.modules[name] = wrap_module(name, self)

    def _apply_site_configuration(self):
        # Gather configuration from the following places (with precedence):
        #   1. $<package.application.name>_SETTINGS_MODULE
        #   2. $ALCHEMIST_SETTINGS_MODULE
        #   3. <project>.settings

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

        # with self.app_context():
        #     # After the initial configuration is gathered; each registered
        #     # package is searched for a settings module or package and that
        #     # is loaded then the site configuration is re-applied (to
        #     # keep precedence).
        #     for package in self.config.get('PACKAGES', ()):
        #         try:
        #             # Attempt to get configuration from the settings module.
        #             self.config.from_object('{}.settings'.format(package))

        #         except ImportError:
        #             # No settings module in package.
        #             pass

        #         try:
        #             # Attempt to import the model module or package.
        #             import_module('{}.models'.format(package))

        #         except ImportError:
        #             # No component in package.
        #             pass

        #         # Re-apply the initial site configuration.
        #         self._apply_site_configuration()

        # # Process database configuration.
        # # Expand each reference into a database engine.
        # # TODO: Support PORT, HOST, USERNAME, and PASSWORD
        # for name in self.config.get('DATABASES', ()):
        #     db = self.config['DATABASES'][name]
        #     if isinstance(db, Mapping):
        #         uri = '{}:///{}'.format(db['engine'], db['name'])
        #         echo = db.get('echo', False)
        #         engine = sa.create_engine(uri, echo=echo)
        #         self.config['DATABASES'][name] = engine

        # # Iterate through the delayed mounts and run each handlers.
        # for handler in self._mounts:
        #     handler()
