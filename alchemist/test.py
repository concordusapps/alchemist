# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from contextlib import contextmanager
from alchemist import db
import requests
import json


@contextmanager
def settings(app, **kwargs):
    """Save current application config and restore after block.

    Allows override with the keyword arguments.
    """

    # Save the current application config to restore.
    _config = dict(app.config)

    # Make requested changes for this scope.
    app.config.update(kwargs)

    yield

    # Restore the previous application config.
    app.config = _config


class TestBase:

    #! Host at which the test server will be intercepted at.
    host = 'localhost'

    #! Port at which the test server will be intercepted at.
    port = 5000

    def setup_class(cls):
        # Create a shortcut for querying because we're all lazy and we
        # know it.
        cls.Q = lambda s, x: db.session.query(x)

    def teardown(self):
        # Rollback the session.
        db.session.rollback()

        # Flush the database access layer.
        db.flush()

        # Commit all of the deletes.
        db.session.commit()

        # TODO: Re-load any desired fixtures.

    def request(self, path='', url=None, data=None, format='json',
                *args, **kwargs):
        # Helper to forward the port and host if url is not specified.
        if url is None:
            url = 'http://{}:{}'.format(self.host, self.port)

        # Get request header dictionary.
        kwargs.setdefault('headers', {})
        headers = kwargs.get('headers')

        # Automatically serialize and send data.
        if format == 'json':
            if data is None:
                data = {}

            kwargs['data'] = json.dumps(data)
            headers.setdefault('Content-Type', 'application/json')

        else:
            kwargs['data'] = data

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
