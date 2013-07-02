# -*- coding: utf-8 -*-
# from .session import Session, session
from .models import Model
from .manager import Manager

import types
import sys
from sqlalchemy import orm


class Session(orm.Session):

    def __init__(self, *args, **kwargs):
        from alchemist.conf import settings
        from alchemist.db.manager import Manager

        # TODO: Support multiple database routing.
        # Bind to the default database.
        kwargs.setdefault('bind', settings['DATABASES']['default'])

        # Bind to the manager class.
        kwargs.setdefault('query_cls', Manager)

        # Continue the initialization.
        super().__init__(*args, **kwargs)



def Package(name):

    # Wrap the module
    class Inner(types.ModuleType):

        __name__ = name

        _session = None

        Session = Session

        Manager = Manager

        Model = Model

        @property
        def session(self):
            from sqlalchemy import orm
            from alchemist.conf import settings

            if self._session is None:
                self._session = self.Session(query_cls=self.Manager)

            return self._session

    # Return the module.
    return Inner(name)


sys.modules['alchemist.db'] = Package('alchemist.db')
