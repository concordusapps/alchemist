# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from alchemist.conf import settings
from sqlalchemy import schema, create_engine
from . import metadata, engine, registry, utils
import sys
import re
from termcolor import cprint
from sqlalchemy_utils import render_expression


def init(names=None, databases=None, echo=False, commit=True, offline=False):
    """Initialize the specified names in the specified databases.

    The general process is as follows:
      - Ensure the database in question exists
      - Ensure all tables exist in the database.

    @param[in] commit
        When False changes are not actually applied.

    @param[in] echo
        When True SQL statements are logged to stdout.

    @param[in] offline
        When True make no connection attempts to the database.
    """

    # Offline preparation cannot commit to the database.

    if offline:
        commit = False

    for table in metadata.sorted_tables:

        # Introspect the table and determine if we are to process it.

        model, component = table.class_, table.class_._component
        model_name = '%s.%s' % (type(model).__module__, type(model).__name__)
        if names and component not in names and model_name not in names:
            continue

        # Determine the target engine from the model.

        target = engine["default"]

        if not offline and table.exists(target):
            continue

        if echo:

            stream = utils.HighlightStream(sys.stdout)
            render_expression('table.create(engine)', engine, stream)

        if commit:

            table.create(target)


def clear(names=None, databases=None, echo=False, commit=True, offline=False):
    """Clear the specified names from the specified databases.

    This can be highly destructive as it destroys tables and when all names
    are removed from a database, the database itself.

    @param[in] commit
        When False changes are not actually applied.

    @param[in] echo
        When True SQL statements are logged to stdout.

    @param[in] offline
        When True make no connection attempts to the database.
    """

    # Offline preparation cannot commit to the database.

    if offline:
        commit = False

    for table in reversed(metadata.sorted_tables):

        # Introspect the table and determine if we are to process it.

        model, component = table.class_, table.class_._component
        model_name = '%s.%s' % (type(model).__module__, type(model).__name__)
        if names and component not in names and model_name not in names:
            continue

        # Determine the target engine from the model.

        target = engine["default"]

        if not offline and not table.exists(target):
            continue

        if echo:

            stream = utils.HighlightStream(sys.stdout)
            render_expression('table.drop(engine)', engine, stream)

        if commit:

            table.drop(target)
