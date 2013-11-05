# -*- coding: utf-8 -*-
import pytest
from alchemist import db
import flask
from wsgi_intercept import add_wsgi_intercept, remove_wsgi_intercept
from wsgi_intercept.requests_intercept import install, uninstall


#! Host at which the test server will bein intercepted at.
HOST = 'localhost'

#! Port at which the test server will being intercepted at.
PORT = 5000


@pytest.fixture(autouse=True, scope='session')
def fixture_server(request):
    # Install the WSGI interception layer.
    install()

    # Enable the WSGI interception layer.
    add_wsgi_intercept(HOST, PORT, lambda: flask.current_app)

    # Add a finalizer to remove the interception layer.
    def finalize():
        remove_wsgi_intercept(HOST, PORT)
        uninstall()

    request.addfinalizer(finalize)


@pytest.fixture(autouse=True, scope='session')
def fixture_database(request):
    # Clear out old database contents.
    db.clear(database=True)

    # Initialize the database access layer.
    db.init(database=True)

    # Ensure we clear out the database at the end.
    def finalizer():
        db.session.rollback()
        db.clear(database=True)

    request.addfinalizer(finalizer)


@pytest.fixture(autouse=True, scope='function')
def fixture_data(request):
    request.addfinalizer(lambda: db.flush())
