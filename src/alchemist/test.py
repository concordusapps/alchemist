# -*- coding: utf-8 -*-
import pytest
import flask
from alchemist import db
from alchemist import commands
from wsgi_intercept import add_wsgi_intercept, remove_wsgi_intercept
from wsgi_intercept.requests_intercept import install_opener, uninstall_opener
import requests


class TestBase:

    #! List of packages used during testing; limits the number of packages
    #! that are reset after each test run.
    #! Default: reset all packages.
    packages = None

    #! Host at which the test server will bein intercepted at.
    host = 'localhost'

    #! Port at which the test server will being intercepted at.
    port = 5000

    @pytest.fixture(autouse=True, scope='class')
    def server(cls, request):
        # Install the WSGI interception layer.
        install_opener()

        # Enable the WSGI interception layer.
        add_wsgi_intercept(cls.host, cls.port, lambda: flask.current_app)

        # Add a finalizer to remove the interception layer.
        def finalize():
            remove_wsgi_intercept(cls.host, cls.port)
            uninstall_opener()

        request.addfinalizer(finalize)

    @pytest.fixture(autouse=True, scope='class')
    def database(cls, request):
        # Initialize the database access layer.
        commands.db.init(names=cls.packages, echo=False)

        # TODO: Load any required fixtures.

    def setup_class(cls):
        # Create a shortcut for querying because we're all lazy and we
        # know it.
        cls.Q = lambda s, x: db.session.query(x)

    def teardown(self):
        # Rollback the session.
        db.session.rollback()

        # Flush the database access layer.
        commands.db.flush(names=self.packages, echo=False)

        # Commit all of the deletes.
        db.session.commit()

        # TODO: Re-load any desired fixtures.

    def request(self, path='', url=None, *args, **kwargs):
        # Helper to forward the port and host if url is not specified.
        if url is None:
            url = 'http://{}:{}'.format(self.host, self.port)

        # Set some defaults for requests.
        kwargs.setdefault('allow_redirects', False)

        # Forward to requests.
        response = requests.request(*args, url=url + path, **kwargs)

        # Re-initialize the thread-local session transaction.
        db.session.commit()

        # Return the response.
        return response

    def head(self, *args, **kwargs):
        kwargs.setdefault('method', 'HEAD')
        return self.request(*args, **kwargs)

    def options(self, *args, **kwargs):
        kwargs.setdefault('method', 'OPTIONS')
        return self.request(*args, **kwargs)

    def get(self, *args, **kwargs):
        kwargs.setdefault('method', 'GET')
        return self.request(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs.setdefault('method', 'POST')
        return self.request(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs.setdefault('method', 'PUT')
        return self.request(*args, **kwargs)

    def patch(self, *args, **kwargs):
        kwargs.setdefault('method', 'PATCH')
        return self.request(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('method', 'DELETE')
        return self.request(*args, **kwargs)
