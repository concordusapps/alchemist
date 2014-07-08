# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext import script
from werkzeug.serving import run_simple


class Server(script.Server):

    name = 'run'

    option_list = script.Server.option_list + (
        script.Option('--mode', '-m', dest='mode',
                      action='store', required=False, default="werkzeug"),
    )

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

    def __call__(self, app, **kwargs):

        # Collect default server configuration from the application config.
        config = app.config
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        kwargs.setdefault('host', config.get('SERVER_HOST', "127.0.0.1"))
        kwargs.setdefault('port', config.get('SERVER_PORT', 5000))
        kwargs.setdefault('use_debugger', config.get('SERVER_DEBUG'))
        kwargs.setdefault('use_reloader', config.get('SERVER_RELOAD'))
        kwargs.setdefault('threaded', config.get('SERVER_THREADED'))
        kwargs.setdefault('processes', config.get('SERVER_PROCESSES', 1))

        # Spin up the server.
        mode = kwargs.get("mode", "werkzeug")
        if mode == "werkzeug":
            processes = kwargs["processes"]
            run_simple(kwargs["host"],
                       kwargs["port"],
                       app,
                       use_debugger=kwargs["use_debugger"],
                       use_reloader=kwargs["use_reloader"],
                       threaded=kwargs["threaded"],
                       processes=(False if processes == 1 else processes))
