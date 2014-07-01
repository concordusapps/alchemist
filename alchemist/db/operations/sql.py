# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from ... import utils
from .. import metadata, engine
from .._engine import clear_cache
from .._session import refresh
from .utils import HighlightStream
from sqlalchemy_utils import (create_mock_engine, create_database,
                              drop_database, database_exists)
import sys


def op(expression, tables=None, test=None, primary=None, secondary=None,
       names=None, echo=False, commit=True,
       offline=False, verbose=False):

    if verbose:
        url = repr(engine['default'].url)
        utils.print_('*', primary, 'default', url)

    # Offline preparation cannot commit to the database and should always
    # echo output.

    if offline:
        commit = False
        echo = True

    for table in (tables or metadata.sorted_tables):

        if not is_table_included(table, names):
            continue

        # Determine the target engine from the model.

        target = engine['default']

        if not offline and test(target, table):
            continue

        if verbose:
            utils.print_('-', secondary, table.name)

        if echo:
            stream = HighlightStream(sys.stdout)
            mock = create_mock_engine(target, stream)
            expression(mock, table)

        if commit:
            expression(target, table)

    # Refresh the session; ensure any further operations succeed in a
    # new context.

    refresh()


def init(**kwargs):
    """Initialize the specified names in the specified databases.

    The general process is as follows:
      - Ensure the database in question exists
      - Ensure all tables exist in the database.
    """

    # TODO: Iterate through all engines in name set.
    database = kwargs.pop('database', False)
    if database and not database_exists(engine['default'].url):
        create_database(engine['default'].url, encoding='utf8')
        clear_cache()

    expression = lambda target, table: table.create(target)
    test = lambda target, table: table.exists(target)
    op(expression, test=test, primary='init', secondary='create', **kwargs)


def clear(**kwargs):
    """Clear the specified names from the specified databases.

    This can be highly destructive as it destroys tables and when all names
    are removed from a database, the database itself.
    """

    database = kwargs.pop('database', False)
    expression = lambda target, table: table.drop(target)
    test = lambda x, tab: not database_exists(x.url) or not tab.exists(x)

    # TODO: Iterate through all engines in name set.
    if database and database_exists(engine['default'].url):
        drop_database(engine['default'].url)
        clear_cache()

    op(expression, reversed(metadata.sorted_tables), test=test,
       primary='clear', secondary='drop', **kwargs)


def flush(**kwargs):
    """Flush the specified names from the specified databases.

    This can be highly destructive as it destroys all data.
    """

    expression = lambda target, table: target.execute(table.delete())
    test = lambda target, table: not table.exists(target)
    op(expression, reversed(metadata.sorted_tables), test=test,
       primary='flush', secondary='flush', **kwargs)


def is_table_included(table, names):
    """Determines if the table is included by reference in the names.

    A table can be named by its component or its model (using the short-name
    or a full python path).

    eg. 'package.models.SomeModel' or 'package:SomeModel' or 'package'
        would all include 'SomeModel'.
    """

    # No names indicates that every table is included.
    if not names:
        return True

    # Introspect the table and pull out the model and component from it.
    model, component = table.class_, table.class_._component

    # Check for the component name.
    if component in names:
        return True

    # Check for the full python name.
    model_name = '%s.%s' % (model.__module__, model.__name__)
    if model_name in names:
        return True

    # Check for the short name.
    short_name = '%s:%s' % (component, model.__name__)
    if short_name in names:
        return True

    return False
