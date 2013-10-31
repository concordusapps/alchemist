# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from ._engine import engine
from ._session import Session, session
from .query import Query
from .model import (Model, _metadata as metadata, _registry_map as registry,
                    _metadata_map as components)
from .operations import (init, clear, flush, status, revision,
                         upgrade, downgrade, history)


__all__ = [
    'engine',
    'Session',
    'session',
    'Query',
    'Model',
    'metadata',
    'components',
    'registry',
    'init',
    'clear',
    'flush',
    'status',
    'revision',
    'upgrade',
    'downgrade',
    'history',
]

# TODO: Support these options perhaps -- look into them at least.
# app.config.setdefault('SQLALCHEMY_NATIVE_UNICODE', None)
# app.config.setdefault('SQLALCHEMY_ECHO', False)
# app.config.setdefault('SQLALCHEMY_RECORD_QUERIES', None)
# app.config.setdefault('SQLALCHEMY_POOL_SIZE', None)
# app.config.setdefault('SQLALCHEMY_POOL_TIMEOUT', None)
# app.config.setdefault('SQLALCHEMY_POOL_RECYCLE', None)
# app.config.setdefault('SQLALCHEMY_MAX_OVERFLOW', None)
# app.config.setdefault('SQLALCHEMY_COMMIT_ON_TEARDOWN', False)
# app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)
