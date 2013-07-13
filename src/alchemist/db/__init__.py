# -*- coding: utf-8 -*-
import types
import sys
import threading


class Module(types.ModuleType):

    #! Locally available session object.
    _local = threading.local()

    @property
    def session(self):
        # Check for an existing session.
        if not hasattr(self._local, 'instance'):
            # No session available; create one.
            self._local.instance = self.Session()

        # Return the available session.
        return self._local.instance

    @property
    def Session(self):
        # Save these for reference.
        from sqlalchemy import orm

        # Construct an inner class to late-bind configuration.
        class Session(orm.Session):

            def __init__(self, *args, **kwargs):
                from alchemist.conf import settings
                from .query import Query

                # Default the bind and query class.
                kwargs.setdefault('bind', settings['DATABASES']['default'])
                kwargs.setdefault('query_cls', Query)

                # Continue the initialization.
                super().__init__(*args, **kwargs)

        # Return the inner class.
        return Session

# Update the inner module with the actual contents.
instance = Module(__name__)
instance.__dict__.update(sys.modules[__name__].__dict__)

# Store the module wrapper
sys.modules[__name__] = instance
