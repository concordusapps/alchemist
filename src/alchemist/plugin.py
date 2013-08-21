# -*- coding: utf-8 -*-
from alchemist import management
import pytest
from alchemist import db, commands
import flask
from wsgi_intercept import add_wsgi_intercept, remove_wsgi_intercept
from wsgi_intercept.requests_intercept import install_opener, uninstall_opener


#! Global application context.
_app_context = None

#! Host at which the test server will bein intercepted at.
HOST = 'localhost'

#! Port at which the test server will being intercepted at.
PORT = 5000


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


@pytest.fixture(autouse=True, scope='session')
def fixture_server(request):
    # Install the WSGI interception layer.
    install_opener()

    # Enable the WSGI interception layer.
    add_wsgi_intercept(HOST, PORT, lambda: flask.current_app)

    # Add a finalizer to remove the interception layer.
    def finalize():
        remove_wsgi_intercept(HOST, PORT)
        uninstall_opener()

    request.addfinalizer(finalize)


@pytest.fixture(autouse=True, scope='session')
def fixture_database(request):
    # TODO: Create testing database.

    # Clear out old database contents.
    commands.db.clear(echo=False)

    # Initialize the database access layer.
    commands.db.init(echo=False)
