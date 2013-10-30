# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext import script


class Server(script.Server):

    name = 'run'

    def __init__(self, *args, **kwargs):

        # Set all defaults to None as they will be defaulted in handle
        # when we have access to an application.
        kwargs.setdefault('port', None)
        kwargs.setdefault('host', None)
        kwargs.setdefault('use_debugger', None)
        kwargs.setdefault('use_reloader', None)
        kwargs.setdefault('threaded', None)
        kwargs.setdefault('processes', None)

        super(Server, self).__init__(*args, **kwargs)

    def handle(self, app, **kwargs):

        # Collect default server configuration from the application config.
        config = app.config
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        kwargs.setdefault('host', config.get('SERVER_HOST'))
        kwargs.setdefault('port', config.get('SERVER_PORT'))
        kwargs.setdefault('use_debugger', config.get('SERVER_DEBUG'))
        kwargs.setdefault('use_reloader', config.get('SERVER_RELOAD'))
        kwargs.setdefault('threaded', config.get('SERVER_THREADED'))
        kwargs.setdefault('processes', config.get('SERVER_PROCESSES'))

        super(Server, self).handle(app, **kwargs)
