# -*- coding: utf-8 -*-
import collections
import sys
import contextlib
from importlib import import_module
import sqlalchemy as sa
from sqlalchemy import schema
from sqlalchemy.orm.query import Query
from flask.ext import script
from termcolor import colored
from alchemist import application
from alchemist.conf import settings
from .utils import print_command


def _render_statement(statement, bind=None):
    """
    Generate an SQL expression string with bound parameters rendered inline
    for the given SQLAlchemy statement.

    Extracted from: <https://gist.github.com/gsakkis/4572159>
    """

    if isinstance(statement, Query):
        if bind is None:
            bind = statement.session.get_bind(
                statement._mapper_zero_or_none())

        statement = statement.statement

    elif bind is None:
        bind = statement.bind

    class LiteralCompiler(bind.dialect.statement_compiler):

        def visit_bindparam(self, bindparam, within_columns_clause=False,
                            literal_binds=False, **kwargs):
            return self.render_literal_value(bindparam.value, bindparam.type)

        def render_literal_value(self, value, type_):
            if isinstance(value, long):
                return str(value)

            elif isinstance(value, (date, datetime)):
                return "'%s'" % value

            return super(LiteralCompiler, self).render_literal_value(
                value, type_)

    return LiteralCompiler(bind.dialect, statement).process(statement)


def limit_metadata(names):
    # Iterate through all registered packages if one is not specified.
    metadata = application.metadata
    if names:
        # Are the names registered?
        metadata = {k: v for k, v in metadata.items() if k in names}
        if not metadata:
            raise ValueError("One of the listed packages is not registered.")

    # Return metadata to use.
    return metadata


def init(names=None, sql=False, echo=True):
    """Initialize the database; create all specified tables."""
    # TODO: Support multi-db routing.
    engine = application.databases['default']

    # Iterate through each collected package metadata.
    for name, metadata in limit_metadata(names).items():
        if echo:
            # Log the sequence.
            print_command('alchemist db', 'init', name)

        # Iterate through all tables.
        for table in metadata.sorted_tables:
            if not table.exists(engine):
                if echo:
                    # Log the sequence.
                    print_command('alchemist db', 'create', table.name,
                                  engine.url.database)

                if sql:
                    # Print the creation statement.
                    print(str(schema.CreateTable(table)) + ';')

                else:
                    # Create the table.
                    table.create(engine)


def clear(names=None, sql=False, echo=True):
    """Clear the database; drop all specified tables."""
    # TODO: Support multi-db routing.
    engine = application.databases['default']

    # Iterate through each collected package metadata.
    for name, metadata in reversed(list(limit_metadata(names).items())):
        if echo:
            # Log the sequence.
            print_command('alchemist db', 'clear', name)

        # Iterate through all tables.
        for table in metadata.sorted_tables:
            if table.exists(engine):
                if echo:
                    # Log the sequence.
                    print_command('alchemist db', 'drop', table.name,
                                  engine.url.database)

                if sql:
                    # Print the creation statement.
                    print(str(schema.DropTable(table)) + ';')

                else:
                    # Create the table.
                    table.drop(engine)


def flush(names=None, sql=False, echo=True):
    """Flush the database; delete data from specified tables."""
    # TODO: Support multi-db routing.
    engine = application.databases['default']

    # Iterate through each collected package metadata.
    for name, metadata in reversed(list(limit_metadata(names).items())):
        if echo:
            # Log the sequence.
            print_command('alchemist db', 'flush', name)

        # Iterate through all tables; deleting those neccessary.
        for table in reversed(metadata.sorted_tables):
            if table.exists(engine):
                # Create the DELETE statement.
                statement = table.delete()

                if echo:
                    # Log the sequence.
                    print_command('alchemist db', 'shell', statement,
                                  engine.url.database)

                if sql:
                    # Log the statement.
                    print(str(_render_statement(statement, bind=engine)) + ';')

                else:
                    with contextlib.closing(engine.connect()) as connection:
                        # Execute the statement.
                        connection.execute(statement)


class Database(script.Manager):

    #! Name of the command as it is invoked on the command line.
    name = 'db'

    def __init__(self, *args, **kwargs):
        # Default the usage description.
        kwargs.setdefault('usage', 'Perform various database operations.')

        # Continue the initialization.
        super().__init__(*args, **kwargs)

        # Add commands.
        for command in [init, clear, flush]:
            # Add the name option to limit operation scope.
            command = self.option(
                dest='names', nargs='*',
                help='The package to perform the operation on; '
                     'defaults to all.')(command)

            # Add the SQL option to print SQL instead.
            command = self.option(
                '-S', '--sql', dest='sql', required=False, default=False,
                action='store_true',
                help='Print the SQL statements to stdout instead '
                     'executing them directly.')(command)
