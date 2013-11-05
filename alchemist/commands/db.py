# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext.script import Command, Option
from alchemist import db


common_options = [
    Option(dest='names', nargs='*',
           help='The names of components or models to limit the scope to.'),
    Option('--echo', action='store_true', required=False, default=False,
           help='Print the SQL statements as they are processed to stdout.'),
    Option('--dry-run', action='store_false', dest='commit',
           required=False, default=True,
           help='Do not commit or finalize any operation.'),
    Option('--offline', action='store_true', required=False, default=False,
           help='Make no connection to the database server.'),
    Option('--quiet', '-q', dest='verbose',
           action='store_false', required=False, default=True),
]


class Initialize(Command):
    """Initialize the database; create all binds and tables.
    """

    name = 'init'

    namespace = 'db'

    option_list = common_options + [
        Option('--database', dest='database',
               action='store_true', required=False, default=False,
               help='Initialize the database before tables.'),
    ]

    def run(self, *args, **kwargs):
        db.init(*args, **kwargs)


class Clear(Command):
    """Clear the database; remove all binds and tables.
    """

    name = 'clear'

    namespace = 'db'

    option_list = common_options + [
        Option('--database', dest='database',
               action='store_true', required=False, default=False,
               help='Clear the database after tables.'),
    ]

    def run(self, *args, **kwargs):
        db.clear(*args, **kwargs)


class Flush(Command):
    """Flush the database; remove all data.
    """

    name = 'flush'

    namespace = 'db'

    option_list = common_options

    def run(self, *args, **kwargs):
        db.flush(*args, **kwargs)


class Shell(Command):
    """Runs the CLI for the specified database.
    """

    name = 'shell'

    namespace = 'db'

    option_list = [
        Option(dest='database', nargs='?', default='default',
               help='The database to drop into the shell for.'),
    ]

    def run(self, *args, **kwargs):
        db.shell(*args, **kwargs)
