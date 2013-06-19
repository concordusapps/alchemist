# -*- coding: utf-8 -*-
import contextlib
# import pkgutil
# from dateutil.parser import parse as parse_datetime
# import json
import colorama
from importlib import import_module
from flask.ext import script


def _db_collect(configuration):
    """Collect all DB metadata from the configuration."""
    # Enumerate through all 'installed' packages.
    bases = {}
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
    return script.Server(host=host, port=port, debug=configuration['DEBUG'])


# def _table_from_package(package, name):
#     models = import_module('{}.models'.format(package))
#     return models.Base._decl_class_registry[name].__table__


# def _default(obj):
#     if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
#         return obj.isoformat()

#     if isinstance(obj, uuid.UUID):
#         return obj.hex

#     if isinstance(obj, bytes):
#         return obj.decode('utf8')

#     # Just give up and stringify it.
#     return str(obj)


# def _dump_one(targets, table):
#     # Establish a database session.
#     session = db.Session()

#     # Select all data.
#     result = session.connection().execute(table.select())

#     # Build result list.
#     for row in result.fetchall():
#         target = {'table': table.name, 'columns': {}}
#         for index, name in enumerate(table.columns.keys()):
#             target['columns'][name] = row[index]

#         targets.append(target)


# @manager.option(dest='names', default=None, nargs='*')
# def dumpdata(names):
#     # Disable INFO.
#     logging.disable(logging.INFO)

#     # Did we get any names?
#     if not names:
#         # Dump everything.
#         names = settings.PACKAGES

#     # Enumerate through tables.
#     targets = []
#     for name in names:
#         # Is this the name of a package ?
#         if name in settings.PACKAGES:
#             # Dump all tables.
#             models = import_module('{}.models'.format(name))
#             for table in models.Base.metadata.sorted_tables:
#                 _dump_one(targets, table)

#         else:
#             # Attempt to get table.
#             table = _table_from_package(*name.split('.'))
#             _dump_one(targets, table)

#     # Dump the JSON
#     print(json.dumps(targets, default=_default))


# def _table_from_name(name):
#     for package in settings.PACKAGES:
#         models = import_module('{}.models'.format(package))
#         if name in models.Base.metadata.tables:
#             return models.Base.metadata.tables[name]


# @manager.command
# def loaddata(name):
#     # Establish a database session.
#     session = db.Session()

#     # Walk all packages and find every `fixtures` directory.
#     name = os.path.join('fixtures', name + '.json')
#     for package in settings.PACKAGES:
#         try:
#             # Attempt to load the text.
#             text = pkgutil.get_data(package, name)

#         except FileNotFoundError:
#             # No file found; move along.
#             continue

#         try:
#             # Attempt to decode the JSON file.
#             data = json.loads(text.decode('utf8'))

#         except ValueError:
#             # Error decoding the JSON file.
#             continue

#         # Iterate through the defined instances.
#         for target in data:
#             # Target should define a table name and a collection
#             # of columns.
#             table = _table_from_name(target['table'])

#             # Attempt to find an existing row.
#             pk_clause = None
#             for key in table.primary_key.columns.keys():
#                 value = target['columns'].get(key)
#                 clause = table.columns[key] == value
#                 pk_clause = (pk_clause & clause) if pk_clause else clause

#             exists = session.connection().execute(
#                 table.select().where(pk_clause)).fetchall()

#             # Prepare values; coerce into python types.
#             values = target['columns']
#             for key, value in values.items():
#                 column = table.columns[key]
#                 kind = column.type.python_type

#                 if (issubclass(kind, datetime.date) or
#                         issubclass(kind, datetime.time)):
#                     # Coerce date/time to python
#                     values[key] = parse_datetime(value)

#                 if issubclass(kind, bytes):
#                     # Encode string as bytes.
#                     values[key] = value.encode('utf8')

#             if exists:
#                 # Update the existing row.
#                 session.connection().execute(table.update().values(
#                     **target['columns']).where(pk_clause))

#             else:
#                 # Add a new row.
#                 session.connection().execute(table.insert().values(
#                     **target['columns']))

#     # Commit the transaction.
#     session.commit()
