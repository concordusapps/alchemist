# -*- coding: utf-8 -*-
import sys
import weakref
import re
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta
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

        # Continue processing.
        super().__init__(name, bases, attrs)


class Model(metaclass=ModelBase):

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        name = cls.__name__.lower()
        name = re.sub(r'([A-Z])', r'_\1', name)
        return name


class Timestamp:
    """Records when a model has been created and updated.
    """

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
