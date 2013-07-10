# -*- coding: utf-8 -*-
import sys
import os
import flask
import contextlib
import traceback
from glob import glob
from importlib import import_module
from itertools import chain
from flask.ext import script
import pkgutil
import colorama
import io
from . import commands


@contextlib.contextmanager
def redirect():
    redirect.stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')

    yield

    sys.stderr.close()
    sys.stderr = redirect.stderr


class Manager(script.Manager):

    _exec_log = []

    @classmethod
    def find_application(cls, path=None, verbose=False):
        # Check in every file in the current directory and every file
        # in every directory in the current directory and the next.
        # If there is no application found, iterate backwards and
        # repeat the process.

        # Get path to use.
        if path is None:
            path = os.getcwd()

        # Perform file globbing.
        globs = chain(glob(os.path.join(path, '*')),
                      glob(os.path.join(path, '*', '*')))

        # Pull list of directories.
        directories = filter(os.path.isdir, globs)
        try:
            # Attempt to walk the directories for packages.
            packages = list(pkgutil.walk_packages(directories))

        except:
            # Failed for some reason or other; move along.
            packages = ()

        # Enumerate through the walked packages.
        for imp, name, is_pkg in packages:
            if name == 'setup' and not is_pkg:
                # Skip setup.py
                continue

            try:
                # Attempt to import the module.
                module = imp.find_module(name).load_module()

            except:
                # Failed for some reason or other; move along.
                cls._exec_log.append(sys.exc_info())

                # Move along and try somewhere else.
                continue

            try:
                # Re-import the module using the standard loader.
                module = import_module(module.__name__)

                # Check for an `.app` or an `.application` in the module.
                app = getattr(module, 'app', None)
                if app is None:
                    app = getattr(module, 'application', None)

            except:
                # Failed for some reason or other; move along.
                # Print the error messages to stderr.
                cls._exec_log.append(sys.exc_info())

                # Die.
                raise

            if app is not None and isinstance(app, flask.Flask):
                # Found the application.
                # Get its directory.
                directory = module.__path__[0]
                if is_pkg:
                    directory = os.path.join(directory, '..')

                # Add the directory to the module path.
                app.config['APP_DIR'] = directory
                sys.path.append(os.path.abspath(directory))

                # Return the application.
                return app

        # Detect if we're root.
        if os.path.dirname(path) == path:
            # Yes; we failed to find an application.
            return

        # Nope; recurse backwards.
        return cls.find_application(path=os.path.dirname(path))

    def create_app(self):
        # We need to attempt to discover one.
        if self._exec_log:
            # Print the error messages.
            for execption in self._exec_log:
                traceback.print_exception(*execption)

            # Exit the process
            sys.exit(1)

        # Return the application.
        return super().create_app()

    def __init__(self, application=None, *args, **kwargs):
        try:
            # Find an application for configuration.
            with redirect():
                application = self.find_application()

        except:
            # Move along; errors were recorded.
            application = flask.Flask('alchemist')

        # Initialize the script manager.
        super().__init__(application, *args, **kwargs)

        # Add default, always-present commands.
        self.add_command(commands.Show)
        self.add_command(commands.Database)
        self.add_command(commands.Shell)
        self.add_command(commands.Test)
        self.add_command(commands.Load)
        # self.add_command(commands.Fixture)

        if application is not None:
            # Add the server command to specifiy the default host and port
            # to be the ones defined in the configuration (if available).
            self.add_command('runserver', script.Server(
                host=application.config.get('SERVER_HOST'),
                port=application.config.get('SERVER_PORT'),
                threaded=True))

        else:
            # Add a basic server.
            self.add_command('runserver', script.Server(threaded=True))

        # # TODO: Add commands from all registered packages.
        # This grabs all `management/commands.py` files and introspects them
        # to find all exposed Command subclasses.

        # Initialize terminal colors for commands and sub-managers.
        colorama.init()

    def add_command(self, command, name=None):
        # Add a named command instance (or sub-manager).
        # Switch the arguments if command is a string (the format
        # expected by flask-script itself).
        if isinstance(command, str):
            command, name = name, command

        # Use the command's defined name (if none is provided).
        if name is None:
            name = command.name

        # Instantiate the command if we were given a type.
        if isinstance(command, type):
            command = command()

        # Continue to add the command.
        super().add_command(name, command)

    def run(self, *args, **kwargs):
        # Ensure we are in the application context while running commands.
        # with self.app.app_context():
        super().run(*args, **kwargs)
