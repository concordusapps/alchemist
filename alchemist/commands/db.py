# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext.script import Command, Option
from alchemist import db


common_options = [
    Option(dest='names', nargs='*'),
    Option('--echo', action='store_true', required=False, default=False),
    Option('--offline', action='store_true', required=False, default=False),
    Option('--dry-run', action='store_false', dest='commit',
           required=False, default=True),
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
