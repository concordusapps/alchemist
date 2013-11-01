# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext.script import Command, Option
from alchemist import db
from termcolor import colored


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

    option_list = common_options

    def run(self, *args, **kwargs):
        db.init(*args, **kwargs)


class Clear(Command):
    """Clear the database; remove all binds and tables.
    """

    name = 'clear'

    namespace = 'db'

    option_list = common_options

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
    """Runs the command-line client for the specified database.
    """

    name = 'shell'

    namespace = 'db'

    option_list = [
        Option(dest='database', nargs='?', default='default',
               help='The database to drop into the shell for.'),
    ]

    def run(self, *args, **kwargs):
        db.shell(*args, **kwargs)


class Status(Command):
    """List the current revision of each database.
    """

    name = 'status'

    namespace = 'db'

    option_list = [
        Option(dest='names', nargs='*',
               help='The names of components to limit the scope to.'),
        Option('--quiet', '-q', dest='verbose',
               action='store_false', required=False, default=True),
    ]

    def run(self, *args, **kwargs):
        db.status(*args, **kwargs)


class Revision(Command):
    """Prepare a new database revision for a component.
    """

    name = 'revision'

    namespace = 'db'

    option_list = [
        Option(dest='component',
               help='The component to generate the revision for.'),
        Option('--message', '-m', dest='message', required=True,
               help='A short message to associate with the revision.'),
        Option('--quiet', '-q', dest='verbose',
               action='store_false', required=False, default=True),
    ]

    def run(self, *args, **kwargs):
        try:
            db.revision(*args, **kwargs)

        except Exception as ex:
            print(colored(' !', 'white', attrs=['dark']),
                  colored('FAIL', 'red', attrs=['bold', 'reverse']),
                  colored(str(ex), 'white'))

            return 1


migration_options = [
    Option(dest='component',
           help='The component to upgrade.'),
    Option(dest='revision',
           help='The revision specifier to upgrade to.'),
    Option('--quiet', '-q', dest='verbose',
           action='store_false', required=False, default=True),
    Option('--offline', action='store_true', required=False, default=False,
           help='Make no connection to the database server.'),
]


class Upgrade(Command):
    """Upgrade a component to a later version.
    """

    name = 'upgrade'

    namespace = 'db'

    option_list = migration_options

    def run(self, *args, **kwargs):
        try:
            db.upgrade(*args, **kwargs)

        except Exception as ex:
            print(colored(' !', 'white', attrs=['dark']),
                  colored('FAIL', 'red', attrs=['bold', 'reverse']),
                  colored(str(ex), 'white'))

            return 1


class Downgrade(Command):
    """Downgrade a component to an earlier version.
    """

    name = 'downgrade'

    namespace = 'db'

    option_list = migration_options

    def run(self, *args, **kwargs):
        try:
            db.downgrade(*args, **kwargs)

        except Exception as ex:
            print(colored(' !', 'white', attrs=['dark']),
                  colored('FAIL', 'red', attrs=['bold', 'reverse']),
                  colored(str(ex), 'white'))

            return 1


class History(Command):
    """List changesets for a component.
    """

    name = 'history'

    namespace = 'db'

    option_list = [
        Option(dest='component',
               help='The component to view the history for.'),
    ]

    def run(self, *args, **kwargs):
        db.history(*args, **kwargs)
