# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from sqlalchemy import orm
from sqlalchemy.ext.declarative.api import DeclarativeMeta


class Query(orm.Query):
    """
    Managed query; allows insertion of methods to the query object via an
    attribute on the model.
    """

    def __new__(cls, entities=None, *args, **kwargs):
        # Find and instantiate the query class defined on the entity.
        entity = entities[-1] if entities else None
        if isinstance(entity, DeclarativeMeta):
            if hasattr(entity, '__query__'):
                # Found a query class; set it.
                cls = entity.__query__

        # Continue as normal.
        return super(Query, cls).__new__(cls)
