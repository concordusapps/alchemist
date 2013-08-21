# -*- coding: utf-8 -*-
import pytest
from alchemist import db, commands, application
import threading
import requests


class TestBase:

    #! Host at which the test server will bein intercepted at.
    host = 'localhost'

    #! Port at which the test server will being intercepted at.
    port = 5000

    def setup_class(cls):
        # Create a shortcut for querying because we're all lazy and we
        # know it.
        cls.Q = lambda s, x: db.session.query(x)

    def teardown(self):
        # Rollback the session.
        db.rollback()

        # Flush the database access layer.
        commands.db.flush(echo=False)

        # Commit all of the deletes.
        db.commit()

        # TODO: Re-load any desired fixtures.

    def request(self, path='', url=None, *args, **kwargs):
        # Helper to forward the port and host if url is not specified.
        if url is None:
            url = 'http://{}:{}'.format(self.host, self.port)

        # Set some defaults for requests.
        kwargs.setdefault('allow_redirects', False)

        # Forward to requests.
        response = requests.request(*args, url=url + path, **kwargs)

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
