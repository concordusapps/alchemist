# -*- coding: utf-8 -*-
from alchemist.management.manager import Manager
import sys


#! Global application context.
_app_context = None


def pytest_configure(config):
    # Configure the project environment; using utilties made available
    # by alchemist.

    # Discover the application that is being tested against.
    application = Manager.find_application()
    if application is not None:
        # Add the path to the module into the system path so that it
        # may be imported.
        sys.path.append(application.__module__)

    # Establish an application context.
    global _app_context
    _app_context = application.app_context()
    _app_context.push()


def pytest_unconfigure(config):
    # Release the application context.
    _app_context.pop()
