# -*- coding: utf-8 -*-
from flask import g, appcontext_tearing_down
from alchemist import app
from werkzeug.local import LocalProxy
import sqlalchemy as sa
from sqlalchemy.orm import Session


# TODO: resolve DATABASE configuration to create appropriate engines
# TODO: discover models using COMPONENTS to create
#   db.metadata and db._decl_class_registry


def create_session():
    engine = sa.create_engine('sqlite:///:memory:')
    return Session(bind=engine)


def _get_session():
    _session = getattr(g, '_session', None)
    if _session is None:
        _session = g._session = create_session()

    return _session


@appcontext_tearing_down.connect
def _teardown_session(*args, **kwargs):
    _session = getattr(g, '_session', None)
    if _session is not None:
        _session.close()


session = LocalProxy(_get_session)
