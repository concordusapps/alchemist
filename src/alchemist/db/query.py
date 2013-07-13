# -*- coding: utf-8 -*-
from sqlalchemy import orm
from sqlalchemy.ext.declarative.api import DeclarativeMeta


class Query(orm.Query):
    """Base query; dervied from the SQLAlchemy query object.
    """

    def __new__(cls, entities, *args, **kwargs):
        # Find and instantiate the query class defined on the entity.
        entity = entities[-1]
        if isinstance(entity, DeclarativeMeta):
            if hasattr(entity, '__query__'):
                # Found a query class; set it.
                cls = entity.__query__

        # Continue as normal.
        return super().__new__(cls)
