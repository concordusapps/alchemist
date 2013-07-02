# -*- coding: utf-8 -*-
import sqlalchemy as sa
from alchemist.conf import settings


class Session(sa.orm.Session):

    def __init__(self, *args, **kwargs):
        # TODO: Support multiple database routing.
        # Bind to the default database.
        kwargs.setdefault('bind', settings['DATABASES']['default'])

        # Continue the initialization.
        super().__init__(*args, **kwargs)
