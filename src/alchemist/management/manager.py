# -*- coding: utf-8 -*-
import sys
import os
import flask
import contextlib
from glob import glob
from importlib import import_module
from itertools import chain
from flask.ext import script
import pkgutil
import colorama
from . import commands


@contextlib.contextmanager
def redirect():
    redirect.stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')

    yield

    sys.stderr.close()
    sys.stderr = redirect.stderr


class Manager(script.Manager):

    @classmethod
    def find_application(cls):
        # Check in every file in the current directory and every file
        # in every directory in the current directory and the next.
        # If there is no application found, iterate backwards and
        # repeat the process.
        directories = filter(os.path.isdir, chain(glob('*'), glob('*/*')))
        try:
            # Attempt to walk the directories for packages.
            packages = list(pkgutil.walk_packages(directories))

        except (SystemError, ImportError, NameError, RuntimeError):
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

            except (SystemError, ImportError, NameError, RuntimeError):
                # Failed for some reason or other; move along.
                continue

            # Re-import the module using the standard loader.
            module = import_module(module.__name__)

            # Check for an `.app` or an `.application` in the module.
            app = getattr(module, 'app', None)
            if app is None:
                app = getattr(module, 'application', None)

            if app is not None and isinstance(app, flask.Flask):
                # Found the application.
                # Get its directory.
                directory = module.__path__[0]
                if is_pkg:
                    directory = os.path.join(directory, '..')

                # Change into its directory
                os.chdir(directory)

                # Return the application.
                return app

        # Detect if we're root.
        cwd = os.getcwd()
        if os.path.dirname(cwd) == cwd:
            # Yes; we failed to find an application.
            return

        # Nope; recurse backwards.
        os.chdir('..')
        return cls.find_application()

    def __init__(self, application=None, *args, **kwargs):
        # If no application is provided; we need to attempt to discover one.
        if application is None:
            with redirect():
                application = self.find_application()

        # If no application is provided; initialize a default one atleast so
        # flask-script doesn't break.
        if application is None:
            application = flask.Flask('alchemist')

        # Initialize the script manager.
        super().__init__(application, *args, **kwargs)

        # Add default, always-present commands.
        self.add_command(commands.Show)
        self.add_command(commands.Database)
        # self.add_command(commands.Shell)
        # self.add_command(commands.Fixture)

        # Add the server command to specifiy the default host and port
        # to be the ones defined in the configuration (if available).
        self.add_command('runserver', script.Server(
            host=self.app.config.get('SERVER_HOST'),
            port=self.app.config.get('SERVER_PORT'),
            threaded=True))

        # TODO: Add commands from all registered packages.
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
        with self.app.app_context():
            super().run(*args, **kwargs)
