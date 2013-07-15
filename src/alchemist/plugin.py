# -*- coding: utf-8 -*-
from alchemist import management
from os import path
import sys


#! Global application context.
_app_context = None


def pytest_configure(config):
    # Configure the project environment; using utilties made available
    # by alchemist.

    # Discover the application that is being tested against.
    application = management.discover()

    # Establish an application context.
    global _app_context
    _app_context = application.app_context()
    _app_context.push()


def pytest_unconfigure(config):
    # Release the application context.
    _app_context.pop()
