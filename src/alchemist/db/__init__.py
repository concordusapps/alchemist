# -*- coding: utf-8 -*-
# from .session import Session, session
import types
import sys
from .models import Model
from .manager import Manager
import threading
from sqlalchemy import orm
from alchemist.conf import settings


# Wrap the module.
class Inner(types.ModuleType):

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
        bind = self.settings['DATABASES']['default']
        Manager = self.Manager

        # Construct an inner class to late-bind configuration.
        class Session(self.orm.Session):

            def __init__(self, *args, **kwargs):
                # Default the bind and query class.
                kwargs.setdefault('bind', bind)
                kwargs.setdefault('query_cls', Manager)

                # Continue the initialization.
                super().__init__(*args, **kwargs)

        # Return the inner class.
        return Session

# Update the inner module with the actual contents.
instance = Inner(__name__)
instance.__dict__.update(sys.modules[__name__].__dict__)

# Store the module wrapper
sys.modules[__name__] = instance
