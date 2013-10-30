# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from . import metadata, engine, utils
import datetime
from os import path
import sys
from termcolor import colored
from contextlib import contextmanager
from sqlalchemy_utils import render_expression, render_statement, mock_engine
from six import print_
import alembic
from alembic import autogenerate
from alembic.util import rev_id, obfuscate_url_pw
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory


def op(expression, tables=metadata.sorted_tables, test=None,
       names=None, databases=None, echo=False, commit=True,
       offline=False, verbose=False):

    if verbose:
        url = obfuscate_url_pw(engine['default'].url)
        print_command(' *', verb, 'default', url)

    # Offline preparation cannot commit to the database and should always
    # echo output.

    if offline:
        commit = False
        echo = True

    for table in tables:

        if not is_table_included(table, names):
            continue

        # Determine the target engine from the model.

        target = engine['default']

        if not offline and test(target, table):
            continue

        if verbose:
            print_command(' -', 'create', table.name)

        if echo:
            stream = utils.HighlightStream(sys.stdout)
            with mock_engine('target', stream):
                expression(engine, table)

        if commit:
            expression(target, table)


def init(**kwargs):
    """Initialize the specified names in the specified databases.

    The general process is as follows:
      - Ensure the database in question exists
      - Ensure all tables exist in the database.
    """
    expression = lambda target, table: table.create(target)
    test = lambda target, table: not table.exists(target)
    op(expression, test=test, **kwargs)


def clear(**kwargs):
    """Clear the specified names from the specified databases.

    This can be highly destructive as it destroys tables and when all names
    are removed from a database, the database itself.
    """
    expression = lambda target, table: table.drop(target)
    test = lambda target, table: table.exists(target)
    op(expression, reversed(metadata.sorted_tables), test=test, **kwargs)


def flush(**kwargs):
    """Flush the specified names from the specified databases.

    This can be highly destructive as it destroys all data.
    """
    expression = lambda target, table: target.execute(table.delete())
    test = lambda target, table: table.exists(target)
    op(expression, reversed(metadata.sorted_tables), test=test **kwargs)



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


def print_command(indicator, name, target, extra):
    print_(colored(indicator, 'white', attrs=['dark']),
           colored(name, 'cyan'),
           colored(target, 'white'),
           colored(extra, 'white', attrs=['dark']),
           file=sys.stderr)


@contextmanager
def _alembic_context(offline=False, **kwargs):
    from alchemist.app import application

    # Build the alembic configuration.
    config = Config()
    config.set_main_option('script_location', application.name)
    config.set_main_option('url', str(engine['default'].url))
    config.set_main_option('revision_environment', 'true')

    # Construct a script directory object.
    script = ScriptDirectory.from_config(config)

    try:
        # Construct an environment context.
        template_args = {'config': config}
        env = EnvironmentContext(
            config, script, as_sql=offline, template_args=template_args,
            **kwargs)

        with env:

            # Configure the environment.
            connection = engine['default'].connect() if not offline else None
            dialect_name = engine['default'].dialect.name
            env.configure(
                connection=connection,
                url=str(engine['default'].url),
                dialect_name=dialect_name,
                target_metadata=metadata)

            # Release control.
            yield env

    finally:
        if not offline:
            connection.close()


def revision(message=None, auto=True):
    """Generate a new database revision.
    """

    with _alembic_context(offline=False) as env:
        context = {}
        script = env.script

        if auto:
            cur = env._migration_context.get_current_revision()
            if script.get_revision(cur) is not script.get_revision("head"):
                raise RuntimeError("Target database is not up to date.")

            autogenerate._produce_migration_diffs(
                env._migration_context, context, [])

        # Generate the revision.
        revid = rev_id()
        current_head = script.get_current_head()
        create_date = datetime.datetime.now()
        revpath = script._rev_path(revid, message, create_date)
        alembic_root = path.dirname(alembic.__file__)
        script._generate_template(
            path.join(alembic_root, 'templates', 'script.py.mako'),
            revpath,
            up_revision=str(revid),
            down_revision=current_head,
            create_date=create_date,
            message=message if message is not None else ("No message"),
            **context)


def upgrade(revision, offline=False):
    """Upgrade the database to a later version.
    """

    starting_rev = None
    if ':' in revision:
        if not offline:
            raise ValueError(
                'Range revision not allowed during offline operation.')

        starting_rev, revision = revision.split(':', 2)

    def process(rev, context):
        return env.script._upgrade_revs(revision, rev)

    with _alembic_context(
            offline=offline,
            starting_rev=starting_rev,
            fn=process,
            destination_rev=revision) as env:

        with env.begin_transaction():
            env.run_migrations()


def status(verbose=False):
    """Display the current revision for each database.
    """

    revisions = {}

    if verbose:
        url = obfuscate_url_pw(engine['default'].url)
        print_(colored(' *', 'white', attrs=['dark']),
               colored('status', 'cyan'),
               colored('default', 'white'),
               colored(url, 'white', attrs=['dark']),
               file=sys.stderr)

    def process(rev, context):
        rev = env.script.get_revision(rev)
        revisions['default'] = rev

        if verbose:
            monkier = 'head' if rev.is_head else ''
            print_(colored(' -', 'white', attrs=['dark']),
                   colored('revision', 'cyan'),
                   colored(rev.revision, 'white'),
                   colored(monkier, 'red', attrs=['bold']),
                   file=sys.stderr)

        return []

    with _alembic_context(fn=process) as env:
        with env.begin_transaction():
            env.run_migrations()

    return revisions


# def current(config, head_only=False):
#     """Display the current revision for each database."""

#     script = ScriptDirectory.from_config(config)
#     def display_version(rev, context):
#         rev = script.get_revision(rev)

#         if head_only:
#             config.print_stdout("%s%s" % (
#                 rev.revision if rev else None,
#                 " (head)" if rev and rev.is_head else ""))

#         else:
#             config.print_stdout("Current revision for %s: %s",
#                                 util.obfuscate_url_pw(
#                                     context.connection.engine.url),
#                                 rev)
#         return []

#     with EnvironmentContext(
#         config,
#         script,
#         fn=display_version
#     ):
#         script.run_env()
