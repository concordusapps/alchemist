 # -*- coding: utf-8 -*-
from collections import defaultdict
from flask.ext import script
from flask.ext.script import Option
import os
import sys
import pkgutil
import glob
import flask
from importlib import import_module
import colorama
from termcolor import colored


def _is_package():
    """Gets if the current directory is a package."""
    # Save the basename (possible package name).
    cwd = os.getcwd()
    name = os.path.basename(cwd)

    # Go back one directory.
    os.chdir('..')

    # Check if any of the found modules match the possible package name.
    result = False
    for _, module_name, is_pkg in pkgutil.iter_modules('.'):
        if module_name == name and is_pkg:
            result = True
            break

    # Return to the previous directory.
    os.chdir(name)
    return result


def discover():
    """
    Discovers the application context to use from traversing the package
    directory structure.

    The algorithm works as follows:
        - If currently in a python package; find the root package.
            > Use the root package `.app` or `.application` object.
        - Else, check all modules in current and sub-directories
          for `.app` or `.application`.
    """

    name = None
    while _is_package():
        # We are in a python package. Iterate back until we are at the
        # root of it.
        name = os.path.basename(os.getcwd())
        os.chdir('..')

    if name is None:
        # Not in a python package; iterate through all modules in the
        # current directory and one-level below each.
        for paths in ['.', (glob.glob('src') + glob.glob('*'))]:
            for imp, module_name, _ in pkgutil.iter_modules(paths):
                if module_name == 'setup':
                    # Don't look at setup.py
                    continue

                m = imp.find_module(module_name).load_module()
                app = getattr(m, 'application', getattr(m, 'app', None))
                if isinstance(app, flask.Flask):
                    # Found an application object.
                    # Add it to the system path.
                    sys.path.append(os.getcwd())

                    # Re-import the module.
                    m = import_module(module_name)

                    # Return the object.
                    return getattr(m, 'application', getattr(m, 'app', None))

        # Still found nothing; give up.
        return None

    # Import the package.
    package = pkgutil.get_importer(os.getcwd()).find_module(name).load_module()
    app = getattr(package, 'application', getattr(package, 'app', None))
    if isinstance(app, flask.Flask):
        # Found an application object.
        # Add it to the system path.
        sys.path.append(os.getcwd())

        # Re-import the module.
        package = import_module(name)

        # Return the object.
        return getattr(package, 'application', getattr(package, 'app', None))


class Command(script.Command):

    #! The defined name to be invoked.
    name = None

    #! The defined namespace of the command.
    #! This is a flexible sub-manager.
    namespace = None

    def log(self, *args):
        name = self.namespace if self.namespace else self.name
        name = 'alchemist %s' % name

        print(colored(name, 'white', attrs=['dark']), *args, file=sys.stderr)

    def warn(self, *args):
        self.log(colored('WARN', 'yellow', attrs=['bold', 'reverse']), *args)

    def fail(self, *args):
        self.log(colored('FAIL', 'red', attrs=['bold', 'reverse']), *args)
        sys.exit(1)


class Manager(script.Manager):

    def __init__(self, *args, **kwargs):
        # Attempt to discover an application.
        app = discover()

        # Set default arguments.
        kwargs.setdefault('with_default_commands', False)

        # Continue initialization.
        super().__init__(app or flask.Flask('alchemist'), *args, **kwargs)

        # Initialize command list.
        self.__commands = []

        # Establish an application context (if we can).
        context = None
        if app is not None:
            context = app.app_context()
            context.push()

        # Add commands from all registered packages.
        packages = app.config.get('PACKAGES', []) if app else ['alchemist']
        for package in packages:
            try:
                # Attempt to load a `.commands` module from the package.
                module = import_module('.commands', package=package)

            except ImportError:
                # No command package.
                continue

            # Iterate through all exposed modules and register anything
            # that looks like a command.
            for name in getattr(module, '__all__', vars(module).keys()):
                obj = getattr(module, name, None)
                if isinstance(obj, type):
                    if (issubclass(obj, script.Manager)
                            or issubclass(obj, script.Command)):
                        # Add the exposed command.
                        self.add_command(obj)

        if context:
            # Release the application context.
            context.pop()

        # Initialize cross-platform terminal colors.
        colorama.init()

    def add_command(self, name, command=None):
        # Allow a 1-argument form of this command where the name
        # is found on the command object as `.name`.
        if command is None:
            command, name = name, None

        # Grab the `.name` on the command or the `__name__` of the
        # command object if not passed a name.
        if name is None:
            name = getattr(command, 'name', command.__name__.lower())

        # Instantiate the command if we were given a type.
        if isinstance(command, type):
            command = command()

        # Add commands to command list.
        self.__commands.append((name, command))

    def handle(self, *args, **kwargs):
        if self.__commands:
            # Resolve command list.
            namespaced_commands = defaultdict(lambda: [])
            for name, command in self.__commands:
                namespace = getattr(command, 'namespace', None)
                if namespace:
                    namespaced_commands[namespace].append((name, command))
                    continue
                super().add_command(name, command)

            # Clear command list.
            self.__commands = []

            # Resolve namespaced commands.
            for namespace in namespaced_commands:
                manager = script.Manager()
                for name, command in namespaced_commands[namespace]:
                    manager.add_command(name, command)
                super().add_command(namespace, manager)

        # Continue on with handling the command.
        super().handle(*args, **kwargs)

    def run(self, *args, **kwargs):
        # Ensure we have an established application context when running
        # commands.
        context = None
        if self.app is not None:
            context = self.app.app_context()
            context.push()

        # Run as normal.
        result = super().run(*args, **kwargs)

        # Release the context.
        if context is not None:
            context.pop

        # Return the result.
        return result


def run(command=None):
    """Simple progammatic execution of the manager."""
    return Manager().handle(sys.argv[0], command or sys.argv[:1])
