# -*- coding: utf-8 -*-
# from .session import Session, session
import types
import sys
from .models import Model
from .manager import Manager
import threading
from sqlalchemy import orm
from alchemist.conf import settings


class Session(orm.Session):

    def __init__(self, *args, **kwargs):
        # TODO: Support multiple database routing.
        # Bind to the default database.
        kwargs.setdefault('bind', settings['DATABASES']['default'])

        # Bind to the manager class.
        kwargs.setdefault('query_cls', Manager)

        # Continue the initialization.
        super().__init__(*args, **kwargs)


# Wrap the module.
class Inner(types.ModuleType):

    #! Locally available session object.
    _local = threading.local()

    @property
    def session(self):
        # Check for an existing session.
        if not hasattr(self._local, 'instance'):
            # No session available; create one.
            self._local.instance = self.orm.Session(
                bind=self.settings['DATABASES']['default'],
                query_cls=self.Manager)

        # Return the available session.
        return self._local.instance

# Update the inner module with the actual contents.
instance = Inner(__name__)
instance.__dict__.update(sys.modules[__name__].__dict__)

# Store the module wrapper
sys.modules[__name__] = instance
