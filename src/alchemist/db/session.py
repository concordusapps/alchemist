# -*- coding: utf-8 -*-
from sqlalchemy import orm
from alchemist.conf import settings
from .manager import Manager


class Session(orm.Session):

    def __init__(self, *args, **kwargs):
        # TODO: Support multiple database routing.
        # Bind to the default database.
        kwargs.setdefault('bind', settings['DATABASES']['default'])

        # Bind to the manager class.
        kwargs.setdefault('query_cls', Manager)

        # Continue the initialization.
        super().__init__(*args, **kwargs)
