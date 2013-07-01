# -*- coding: utf-8 -*-
import contextlib
import datetime
import uuid
import operator
import pkgutil
import os
import collections
import logging
from functools import reduce
from dateutil.parser import parse as parse_datetime
import json
import colorama
from importlib import import_module
from flask.ext import script


def _db_collect(configuration):
    """Collect all DB metadata from the configuration."""
    # Enumerate through all 'installed' packages.
    bases = collections.OrderedDict()
    for name in configuration['PACKAGES']:
        try:
            # Attempt to import the model file.
            models = import_module('{}.models'.format(name))

        except ImportError:
            # No installed models; move along.
            continue

        # Append the model bases.
        bases[name] = models.Base

    # Return the bases.
    return bases


def _db_flush_one(metadata, engine):
    """Delete all data from the database."""
    with contextlib.closing(engine.connect()) as connection:
        transaction = connection.begin()
        for table in reversed(metadata.sorted_tables):
            connection.execute(table.delete())
        transaction.commit()


def Database(configuration):
    # Instantiate a second-level management application for the database.
    Database = script.Manager(usage="Perform various database operations.")

    # Collect the db metadata.
    bases = _db_collect(configuration)

    @Database.command
    def init():
        """Initialize the database and create all neccessary tables."""
        for base in bases.values():
            base.metadata.create_all(configuration['DATABASE_ENGINE'])

    @Database.command
    def flush():
        """Initialize the database and create all neccessary tables."""
        for base in bases.values():
            _db_flush_one(base.metadata, configuration['DATABASE_ENGINE'])

    @Database.command
    def clear():
        """Drop all database tables."""
        for base in bases.values():
            base.metadata.drop_all(configuration['DATABASE_ENGINE'])

    # Return the database management command.
    return Database


def _make_context_one(ctx, name, base):
    items = []
    for cls in base._decl_class_registry.values():
        if isinstance(cls, type):
            items.append(cls.__name__)
            ctx[cls.__name__] = cls

    print(
        colorama.Fore.GREEN + colorama.Style.DIM +
        "from {}.models import {}".format(
            name, ', '.join(items)) + colorama.Style.RESET_ALL)


def _make_context(configuration):
    # Initialize colorama.
    colorama.init()

    # Start by adding the session instance to the user's namespace.
    namespace = {'session': configuration['DATABASE_SESSION']()}
    print(colorama.Fore.GREEN + colorama.Style.DIM +
          "from {}.db import Session".format(__package__))
    print("session = Session()")

    # Collect all the models and add those to the namespace.
    for name, base in _db_collect(configuration).items():
        _make_context_one(namespace, name, base)

    # Return the context.
    return namespace


def Shell(configuration):
    # Create the shell with a make_context method that draws from
    # all available models.
    return script.Shell(make_context=lambda: _make_context(configuration))


def Server(configuration):
    # Create a runserver command that uses settings for its host and port.
    host = configuration['SERVER_HOST']
    port = configuration['SERVER_PORT']
    return script.Server(host=host, port=port, debug=configuration['DEBUG'],
                         threaded=True)


class Fixture:

    class Load(script.Command):

        option_list = (
            script.Option(dest='name'),
        )

        def __init__(self, config):
            super().__init__()

            # Store the configuration for later use.
            self.config = config

        def run(self, name):
            # Establish a database session.
            session = self.config['DATABASE_SESSION']()

            try:
                # Attempt to open the name directly as a file.
                with open(name) as stream:
                    self._load_one(session, stream.read())

                # Commit the transaction.
                session.commit()

                # We're done here.
                return

            except FileNotFoundError:
                # Not a file.
                pass

            # Iterate through all packages.
            name = os.path.join('fixtures', name) + '.json'
            for package in self.config['PACKAGES']:
                try:
                    # Attmept to pull the fixture from here.
                    text = pkgutil.get_data(package, name).decode('utf8')

                except FileNotFoundError:
                    # No file found; move along.
                    continue

                # Load this fixture.
                self._load_one(session, text)

            # Commit the transaction.
            session.commit()

        def _get_table(self, name):
            for package in self.config['PACKAGES']:
                try:
                    # Attempt to get models.
                    models = import_module('{}.models'.format(package))

                except ImportError:
                    # Package doesn't have models.
                    continue

                if name in models.Base.metadata.tables:
                    return models.Base.metadata.tables[name]

        def _load_one(self, session, text):
            # Decode the JSON.
            data = json.loads(text)

            # Iterate through the defined instances.
            for target in data:
                # Target should define a table name and a collection
                # of columns.
                table = self._get_table(target['table'])

                # Build the primary key clause.
                c = target['columns']
                values = map(lambda x: x == c[x.name], table.primary_key)
                clause = reduce(operator.and_, values)

                # Attempt to find an existing row.
                exists = session.connection().execute(
                    table.select().where(clause).limit(1)).first()

                # Prepare values; coerce into python types.
                for key, value in target['columns'].items():
                    kind = table.columns[key].type.python_type

                    if (issubclass(kind, datetime.date)
                            or issubclass(kind, datetime.time)):
                        # Coerce date/time to python
                        target['columns'][key] = parse_datetime(value)

                    elif issubclass(kind, bytes):
                        # Encode string as bytes.
                        target['columns'][key] = value.encode('utf8')

                if exists:
                    # Update the existing row.
                    statement = table.update().values(
                        **target['columns']).where(clause)

                else:
                    # Add a new row.
                    statement = table.insert().values(**target['columns'])

                # Execute the statement.
                session.connection().execute(statement)

    class Dump(script.Command):

        option_list = (
            script.Option(dest='names', default=None, nargs='*'),
        )

        def __init__(self, config):
            super().__init__()

            # Store the configuration for later use.
            self.config = config

        def run(self, names):
            # Disable INFO (sqlalchemy log level).
            logging.disable(logging.INFO)

            # Dump all the things if we didn't get any names.
            packages = self.config.get('PACKAGES', [])
            if not names:
                names = packages

            # Enumerate through the packages and tables.
            targets = []
            for name in names:
                if name in packages:
                    try:
                        # Dump all tables in package.
                        models = import_module('{}.models'.format(name))

                    except ImportError:
                        # No models here
                        continue

                    for table in models.Base.metadata.sorted_tables:
                        self._dump_one(targets, table)

                else:
                    # Dump this specific table.
                    segments = name.split('.')
                    table = segments[-1]
                    package = '.'.join(segments[:-1])
                    self._dump_one(targets, self._get_table(package, table))

            # Dump the JSON
            print(json.dumps(targets, default=self._default))

        @staticmethod
        def _get_table(package, name):
            models = import_module('{}.models'.format(package))
            return models.Base._decl_class_registry[name].__table__

        def _dump_one(self, targets, table):
            # Establish a database session.
            session = self.config['DATABASE_SESSION']()

            # Select all data.
            result = session.connection().execute(table.select())

            # Build result list.
            for row in result.fetchall():
                target = {'table': table.name, 'columns': {}}
                for index, name in enumerate(table.columns.keys()):
                    target['columns'][name] = row[index]

                targets.append(target)

        @staticmethod
        def _default(obj):
            if (isinstance(obj, datetime.time)
                    or isinstance(obj, datetime.date)):
                return obj.isoformat()

            if isinstance(obj, uuid.UUID):
                return obj.hex

            if isinstance(obj, bytes):
                return obj.decode('utf8')

            # Just give up and stringify it.
            return str(obj)
