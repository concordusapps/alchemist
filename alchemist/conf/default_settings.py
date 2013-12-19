# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from alchemist.conf import defer

# Debugging.
DEBUG = True

# Default server configuration.
SERVER_HOST = '::1'
SERVER_PORT = 8000
SERVER_DEBUG = defer('DEBUG')
SERVER_RELOAD = defer('DEBUG')
SERVER_THREADED = False
SERVER_PROCESSES = 1

# List of registered components.
COMPONENTS = ['alchemist']

# Default metaclass to use for the declarative extension with SQLAlchemist.
MODEL_METACLASS = 'sqlalchemy.ext.declarative.api.DeclarativeMeta'
