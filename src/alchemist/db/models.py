# -*- coding: utf-8 -*-
import sys
import weakref
import re
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import object_session
from sqlalchemy.orm.util import has_identity
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta, base
from alchemist.conf import settings


class ModelBase(DeclarativeMeta):

    #! The metadata.
    metadata = sa.MetaData()

    @property
    def _decl_class_registry(self):
        """Retrieves the scoped class registry, if available."""
        return getattr(self, '_class_registry', None)

    #! Dictionary of metadata classes; keyed by package.
    _metadata = {}

    #! Dictionary of class registries; keyed by package.
    _registry = {}

    @staticmethod
    def _get_package(module):
        # Get the registered package this model belongs to.
        package = module.split('.')
        while package:
            # Is this name a registered package?
            test = '.'.join(package)
            if test in settings['PACKAGES']:
                # This is the package we are in.
                return test

            # Remove the right-most segment.
            package.pop()

        if not package:
            # No package was found to be registered; attempt to guess the
            # right package name; strip all occurrances of '.models' from the
            # pacakge name.
            return module.replace('.models', '')

    @staticmethod
    def _is_match(bases):
        for base in bases:
            if isinstance(base, ModelBase):
                # This is twice derived.
                return True

        # Nope; this is the base.
        return False

    @property
    def objects(self):
        """Create an object session and return the query object."""
        return __import__('alchemist.db').db.session.query(self)

    def __new__(cls, name, bases, attrs):
        # Don't process further if this is the base.
        if not cls._is_match(bases):
            return super().__new__(cls, name, bases, attrs)

        # Check for existing metadata.
        package = cls._get_package(attrs['__module__'])
        if package not in cls._registry:
            cls._registry[package] = weakref.WeakValueDictionary()

        # Set new registry.
        attrs['_class_registry'] = cls._registry[package]

        # Continue processing.
        return super().__new__(cls, name, bases, attrs)

    def __init__(self, name, bases, attrs):
        # Don't process further if this is the base.
        if not self._is_match(bases):
            return super().__init__(name, bases, attrs)

        # Check for existing metadata.
        package = self._get_package(attrs['__module__'])
        if package not in self._metadata:
            self._metadata[package] = sa.MetaData()

        # Add metadata and registry to the attributes.
        self.metadata = attrs['metadata'] = self._metadata[package]

        # Attach the declarative initialization routine.
        self.__init__ = attrs['__init__'] = base._declarative_constructor

        # Continue processing.
        super().__init__(name, bases, attrs)


class Model(metaclass=ModelBase):

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        package = ModelBase._get_package(cls.__module__).lower()
        name = '{}.{}'.format(package, cls.__name__.lower())
        name = re.sub(r'([A-Z])', r'_\1', name)
        name = re.sub(r'\.+', r'_', name)
        return name

    def save(self):
        """Commit helper; akin to django's model.save()"""
        if has_identity(self):
            # Object has already been persisted to the database.
            # Commit any changes that may have happened.
            session = object_session(self)
            session.commit()

        else:
            from alchemist import db

            # Object has not been persisted to the database.
            # Add it to the scoped session and commit it.
            db.session.add(self)
            db.session.commit()


class Timestamp(Model):
    """Records when a model has been created and updated.
    """

    __abstract__ = True

    created = sa.Column(
        sa.DateTime, default=datetime.utcnow, nullable=False,
        doc='Date and time the model was created.')

    updated = sa.Column(
        sa.DateTime, default=datetime.utcnow, nullable=False,
        doc='Date and time the model was last updated.')


@sa.event.listens_for(Timestamp, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    # When a model with a timestamp is updated; force update the updated
    # timestamp.
    target.updated = datetime.utcnow()
