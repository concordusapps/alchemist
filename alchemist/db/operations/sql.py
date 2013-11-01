# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from .. import metadata, engine, utils
import sys
from termcolor import colored
from sqlalchemy_utils import create_mock_engine
from six import print_
from alembic.util import obfuscate_url_pw


def op(expression, tables=None, test=None, primary=None, secondary=None,
       names=None, databases=None, echo=False, commit=True,
       offline=False, verbose=False):

    if verbose:
        url = obfuscate_url_pw(engine['default'].url)
        print_command(' *', primary, 'default', url)

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
            print_command(' -', secondary, table.name)

        if echo:
            stream = utils.HighlightStream(sys.stdout)
            mock = create_mock_engine(target, stream)
            expression(mock, table)

        if commit:
            expression(target, table)


def init(**kwargs):
    """Initialize the specified names in the specified databases.

    The general process is as follows:
      - Ensure the database in question exists
      - Ensure all tables exist in the database.
    """
    expression = lambda target, table: table.create(target)
    test = lambda target, table: table.exists(target)
    op(expression, test=test, primary='init', secondary='create', **kwargs)


def clear(**kwargs):
    """Clear the specified names from the specified databases.

    This can be highly destructive as it destroys tables and when all names
    are removed from a database, the database itself.
    """
    expression = lambda target, table: table.drop(target)
    test = lambda target, table: not table.exists(target)
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


def print_command(indicator, name, target='', extra=''):
    print_(colored(indicator, 'white', attrs=['dark']),
           colored(name, 'cyan'),
           colored(target, 'white'),
           colored(extra, 'white', attrs=['dark']),
           file=sys.stderr)
