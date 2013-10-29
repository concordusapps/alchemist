# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from alembic.util import obfuscate_url_pw
from sqlalchemy_utils import render_expression
from .. import engine, metadata
from . import utils
import sys


def init(names=None, databases=None, echo=False, commit=True, offline=False,
         verbose=False):
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

    if verbose:
        url = obfuscate_url_pw(engine['default'].url)
        utils.print_command(' *', 'init', 'default', url)

    # Offline preparation cannot commit to the database and should always
    # echo output.

    if offline:
        commit = False
        echo = True

    for table in metadata.sorted_tables:

        if not utils.is_table_included(table, names):
            continue

        # Determine the target engine from the model.

        target = engine['default']

        if not offline and table.exists(target):
            continue

        if verbose:
            utils.print_command(' -', 'create', table.name)

        if echo:
            stream = utils.HighlightStream(sys.stdout)
            render_expression('table.create(engine)', engine, stream)

        if commit:
            table.create(target)
