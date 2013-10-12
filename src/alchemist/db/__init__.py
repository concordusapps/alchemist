# -*- coding: utf-8 -*-
from ._engine import engine
from ._session import Session, session
from .query import Query


__all__ = [
    'engine',
    'Session',
    'session',
    'Query',
]

# TODO: Support these options perhaps -- look into them at least.
# app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite://')
# app.config.setdefault('SQLALCHEMY_BINDS', None)
# app.config.setdefault('SQLALCHEMY_NATIVE_UNICODE', None)
# app.config.setdefault('SQLALCHEMY_ECHO', False)
# app.config.setdefault('SQLALCHEMY_RECORD_QUERIES', None)
# app.config.setdefault('SQLALCHEMY_POOL_SIZE', None)
# app.config.setdefault('SQLALCHEMY_POOL_TIMEOUT', None)
# app.config.setdefault('SQLALCHEMY_POOL_RECYCLE', None)
# app.config.setdefault('SQLALCHEMY_MAX_OVERFLOW', None)
# app.config.setdefault('SQLALCHEMY_COMMIT_ON_TEARDOWN', False)
# app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)
