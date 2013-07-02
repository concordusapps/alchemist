# -*- coding: utf-8 -*-
import types
from sqlalchemy.orm import object_session
from sqlalchemy.orm.query import Query
from sqlalchemy.ext.declarative.api import DeclarativeMeta


class Manager(Query):
    """Base object manager; dervied from the SQLAlchemy query object.

    The following was extracted from:
    <https://github.com/d1ffuz0r/sqlalchemy-manager/blob/master/alchmanager.py>
    """

    def __init__(self, entities, *args, **kwargs):
        # TODO: Look at joins.. it looks like just the first manager
        #   is taken.
        # Find and apply an object manager defined on the object entity.
        self.entity = entity = entities[0]
        not_private = lambda name: not name.startswith('_')
        if isinstance(entity, DeclarativeMeta):
            if hasattr(entity, '__manager__'):
                manager_cls = entity.__manager__
                for fname in filter(not_private, dir(manager_cls)):
                    fn = getattr(manager_cls, fname)
                    try:
                        setattr(self, fname, types.MethodType(fn, self))

                    except TypeError:
                        # Not callable; keep going.
                        continue

        # Continue the initialization.
        super(Manager, self).__init__(entities, *args, **kwargs)


    def create(self, *args, **kwargs):
        """
        Creation helper; creates an instance of the left-most table with
        the passed arguments (forwarded to the initialization routine).
        """
        # Create the target instance.
        target = self.entity(*args, **kwargs)

        # Add the target to the session and commit the session.
        self.session.add(target)
        self.session.commit()

        # Return the created instance.
        return target
