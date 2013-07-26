# -*- coding: utf-8 -*-
from flask.ext import script
from alchemist.conf import settings


class Server(script.Server):
    """Runs the application server for development use.
    """

    name = 'run'

    def __init__(self, *args, **kwargs):
        # Pull server configuration out of configuration.
        server = settings.get('SERVER', {})
        server['host'] = server.get('host', 'localhost')
        server['port'] = server.get('port', 8000)
        server['threaded'] = server.get('threaded', True)

        # Default the server configuration for flask-script.
        kwargs.update(server)

        # Continue initialization.
        super().__init__(*args, **kwargs)
