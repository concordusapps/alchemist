# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from .. import engine
import os


def shell(database='default'):
    """Runs the command-line client for the specified database.
    """

    target = engine[database]
    dialect = engine[database].dialect.name

    if dialect == 'mysql':
        args = ['mysql']

        if target.url.username:
            args += ['--user=%s' % target.url.username]

        if target.url.password:
            args += ['--password=%s' % target.url.password]

        if 'unix_socket' in target.url.query:
            args += ["--socket=%s" % target.url.query['unix_socket']]

        elif target.url.host:
            args += ["--host=%s" % target.url.host]

            if target.url.port:
                args += ["--port=%s" % target.url.port]

        if target.url.database:
            args += [target.url.database]

    elif dialect == 'sqlite':
        args = ['sqlite3', target.url.database]

    else:  # pragma: nocoverage
        raise RuntimeError(
            'Database shell not available for the dialect %r' % dialect)

    os.execvp(args[0], args)
