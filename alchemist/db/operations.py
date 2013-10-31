# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from . import metadata, engine, utils, components
import datetime
from importlib import import_module
import sqlalchemy as sa
import os
from os import path
import sys
from hashlib import md5
from termcolor import colored
from contextlib import closing, contextmanager
from sqlalchemy_utils import create_mock_engine
from sqlalchemy.engine import url as sqla_url
from sqlalchemy.sql import select
from six import print_
from collections import OrderedDict
from alchemist.conf import settings
import alembic
from alembic import autogenerate, migration
from alembic.util import rev_id, obfuscate_url_pw, template_to_file
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory


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


@contextmanager
def alembic_env(component, offline=False, init=False, **kwargs):

    # Retrieve the component metadata, if any.
    md = components[component] if component in components else None

    # Find and create the script directory if neccessary.
    location = path.dirname(import_module(component).__file__)
    versions = path.join(location, 'versions')
    if init and not path.exists(versions):
        os.makedirs(versions)

    # Build the configuration object.
    config = Config()
    config.set_main_option('script_location', location)
    config.set_main_option('url', str(engine['default'].url))
    config.set_main_option('revision_environment', 'true')

    # Construct the script directory object from the configuration.
    script = ScriptDirectory.from_config(config)

    # Construct the environment context.
    template_args = {'config': config}
    env = EnvironmentContext(
        config, script, as_sql=offline,
        template_args=template_args, **kwargs)

    def patch(env):
        # Monkey patch the migration context.
        env._migration_context = MigrationContext.configure(
            component,
            connection=env._migration_context.connection,
            url=options['url'],
            dialect_name=options['dialect_name'],
            opts=env.context_opts)

    # Prepare options for the environment.
    options = {
        'url': str(engine['default'].url),
        'dialect_name': engine['default'].dialect.name,
        'target_metadata': md}

    if offline:
        with env:
            env.configure(**options)
            patch(env)
            yield env

    else:
        connection = engine['default'].connect()
        with closing(connection):
            with env:
                env.configure(connection=connection, **options)
                patch(env)
                yield env


class MigrationContext(migration.MigrationContext):

    def __init__(self, component, *args, **kwargs):
        self.__component = component.encode('utf8')
        super(MigrationContext, self).__init__(*args, **kwargs)
        self._version = sa.Table(
            'alchemist_versions', sa.MetaData(),
            sa.Column('component_id', sa.String(32), nullable=False),
            sa.Column('version_num', sa.String(32), nullable=False),
            schema=self._version.schema)

    @classmethod
    def configure(cls, component, connection=None, url=None, dialect_name=None,
                  opts=None):
        if connection:
            dialect = connection.dialect
        elif url:
            url = sqla_url.make_url(url)
            dialect = url.get_dialect()()
        elif dialect_name:
            url = sqla_url.make_url("%s://" % dialect_name)
            dialect = url.get_dialect()()
        else:
            raise Exception("Connection, url, or dialect_name is required.")

        return cls(component, dialect, connection, opts)

    def get_current_revision(self):
        """Return the current revision, usually that which is present
        in the ``alembic_version`` table in the database.

        If this :class:`.MigrationContext` was configured in "offline"
        mode, that is with ``as_sql=True``, the ``starting_rev``
        parameter is returned instead, if any.

        """
        if self.as_sql:
            return self._start_from_rev
        else:
            if self._start_from_rev:
                raise RuntimeError(
                    "Can't specify current_rev to context "
                    "when using a database connection")
            self._version.create(self.connection, checkfirst=True)
        component_id = md5(self.__component).hexdigest()
        q = self._version.c.component_id == component_id
        stmnt = select([self._version.c.version_num]).where(q)
        return self.connection.scalar(stmnt)

    def _update_current_rev(self, old, new):
        cid = md5(self.__component).hexdigest()
        if old == new:
            return
        if new is None:
            self.impl._exec(self._version.delete())
        elif old is None:
            self.impl._exec(self._version.insert().
                        values(component_id=sa.literal_column("'%s'" % cid),
                               version_num=sa.literal_column("'%s'" % new))
                    )
        else:
            self.impl._exec(self._version.update().
                        values(component_id=sa.literal_column("'%s'" % cid),
                               version_num=sa.literal_column("'%s'" % new))
                    )


def revision(component, message=None, auto=True, verbose=False):
    """Generate a new database revision for a component.
    """

    with alembic_env(component, offline=False, init=True) as env:
        context = {}
        script = env.script

        if auto:
            cur = env._migration_context.get_current_revision()
            if script.get_revision(cur) is not script.get_revision("head"):
                raise RuntimeError("Target component is not up to date.")

            autogenerate._produce_migration_diffs(
                env._migration_context, context, set([]))

        # Generate the revision.
        revid = rev_id()
        current_head = script.get_current_head()
        create_date = datetime.datetime.now()
        revpath = script._rev_path(revid, message, create_date)
        alembic_root = path.dirname(alembic.__file__)
        source = path.join(alembic_root, 'templates/generic/script.py.mako')
        template_to_file(
            source, revpath,
            up_revision=str(revid),
            down_revision=current_head,
            create_date=create_date,
            message=message if message is not None else ("No message"),
            **context)


def upgrade(component, revision, offline=False, verbose=False):
    """Upgrade the component to a later version.
    """

    starting_rev = None
    if ':' in revision:
        if not offline:
            raise ValueError(
                'Range revision not allowed during online operation.')

        starting_rev, revision = revision.split(':', 2)

    def process(rev, context):
        return env.script._upgrade_revs(revision, rev)

    with alembic_env(
            component,
            offline=offline,
            starting_rev=starting_rev,
            fn=process,
            destination_rev=revision) as env:

        with env.begin_transaction():
            env.run_migrations()


def downgrade(component, revision, offline=False, verbose=False):
    """Downgrade the component to a later version.
    """

    starting_rev = None
    if ':' in revision:
        if not offline:
            raise ValueError(
                'Range revision not allowed during online operation.')

        starting_rev, revision = revision.split(':', 2)

    elif offline:
        raise ValueError("downgrade with --offline requires <fromrev>:<torev>")

    def process(rev, context):
        return env.script._downgrade_revs(revision, rev)

    with alembic_env(
            component,
            offline=offline,
            starting_rev=starting_rev,
            fn=process,
            destination_rev=revision) as env:

        with env.begin_transaction():
            env.run_migrations()


def status(names=None, verbose=False):
    """Display the current revision for each component.
    """

    revisions = OrderedDict()
    components = settings.get('COMPONENTS', [])
    for component in components:

        if names and component not in names:
            continue

        def process(rev, context):
            rev = env.script.get_revision(rev)
            revisions[component] = rev or 'base'
            return []

        with alembic_env(component, fn=process, offline=False) as env:
            with env.begin_transaction():
                try:
                    env.run_migrations()

                except FileNotFoundError:
                    revisions[component] = None

    for name, revision in revisions.items():
        print_command(' *', 'status', name, revision or 'unversioned')

    return revisions


def history(component, rev_range=None):
    """List changeset scripts in chronological order.
    """

    if rev_range is not None:
        if ":" not in rev_range:
            raise util.CommandError(
                    "History range requires [start]:[end], "
                    "[start]:, or :[end]")
        base, head = rev_range.strip().split(":")
    else:
        base = head = None

    with alembic_env(component, offline=False) as env:

        for sc in env.script.walk_revisions(
                base=base or 'base', head=head or 'head'):
            if sc.is_head:
                env.config.print_stdout("")
            env.config.print_stdout(sc.log_entry)
