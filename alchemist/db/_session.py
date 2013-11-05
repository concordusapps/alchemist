# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from . import engine, query
from flask import appcontext_tearing_down, g
from sqlalchemy import orm
from werkzeug import LocalProxy


class Session(orm.Session):

    def __init__(self, **kwargs):

        # Default the bind and query class.

        # TODO: Serisouly consider using autocommit.
        #http://docs.sqlalchemy.org/en/rel_0_8/orm/session.html#autocommit-mode

        kwargs.setdefault('autocommit', False)
        kwargs.setdefault('autoflush', True)
        kwargs.setdefault('query_cls', query.Query)

        # Bind to the default database engine for now.
        # Once we have db.Model built we can ask that what to bind to
        # upon operation.

        # NOTE: We sub into engine instead of just letting it be because
        # we want to raise as soon as possible if the user forgot their
        # config.

        kwargs.setdefault('bind', engine['default'])

        super(Session, self).__init__(**kwargs)

    def __repr__(self):
        return '<Session(bind=%r)>' % self.bind


def _get_session():
    _session = getattr(g, '_session', None)
    if _session is None:
        _session = g._session = Session()

    return _session


@appcontext_tearing_down.connect
def _teardown_session(*args, **kwargs):
    """
    Ensure the session is closd on the application context teardown which
    happens on the end of a request or interactive session.

    This ensures that the database connnection is closed appropriately.
    """

    _session = getattr(g, '_session', None)
    if _session is not None:
        _session.close()


session = LocalProxy(_get_session)


def refresh():
    if session:
        session.expire_all()
        session.expunge_all()
        session.commit()
