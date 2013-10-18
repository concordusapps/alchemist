# -*- coding: utf-8 -*-
from flask.ext import script


class Server(script.Server):

    name = 'runserver'

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
        kwargs.setdefault('host', config.get('SERVER_HOST', '::1'))
        kwargs.setdefault('port', config.get('SERVER_PORT', 8000))
        kwargs.setdefault('use_debugger', config.get('SERVER_DEBUG', True))
        kwargs.setdefault('use_reloader', config.get('SERVER_RELOAD', True))
        kwargs.setdefault('threaded', config.get('SERVER_THREADED', False))
        kwargs.setdefault('processes', config.get('SERVER_PROCESSES', 1))

        super(Server, self).handle(app, **kwargs)
