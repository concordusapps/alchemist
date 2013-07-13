# -*- coding: utf-8 -*-
import weakref
import re
import sqlalchemy as sa
from sqlalchemy.orm import object_session
from sqlalchemy.orm.util import has_identity
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta, base
from alchemist.conf import settings


def _package_of(module):
    """Gets the root package name of the passed `models` package.
    """

    # Get the registered package this model belongs to.
    package = module.split('.')
    while package:
        # Is this name a registered package?
        test = '.'.join(package)
        if test in settings.get('PACKAGES', []):
            # This is the package we are in.
            return test

        # Remove the right-most segment.
        package.pop()

    if not package:
        # No package was found to be registered; attempt to guess the
        # right package name; strip all occurrances of '.models' from the
        # pacakge name.
        return module.replace('.models', '')


#! Dictionary of metadata classes; keyed by package.
_model_metadata = {}


#! Dictionary of class registries; keyed by package.
_model_registry = {}


class ModelBase(DeclarativeMeta):

    @property
    def _decl_class_registry(self):
        return getattr(self, '_registry', None)

    @property
    def query(self):
        """Create an object session and return the query object."""
        return __import__('alchemist.db').db.session.query(self)

    def __new__(cls, name, bases, attrs):
        # Don't process further if this is the base.
        for base in bases:
            if isinstance(base, ModelBase):
                # This is twice derived.
                break

        # Nope; this is the base.
        else:
            return super().__new__(cls, name, bases, attrs)

        # Check for existing metadata.
        package = _package_of(attrs['__module__'])
        if package not in _model_registry:
            _model_registry[package] = weakref.WeakValueDictionary()
            _model_metadata[package] = sa.MetaData()

        # Set new registry.
        attrs['_registry'] = _model_registry[package]

        # Add metadata and registry to the attributes.
        attrs['metadata'] = _model_metadata[package]

        # Continue processing.
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=ModelBase):
    """Declares the base model.

    This provides various helpers, defaults, and utilities for
    sqlalchemy-derived models.
    """

    __abstract__ = True

    __init__ = base._declarative_constructor

    @declared_attr
    def __tablename__(cls):
        """
        Underscorizes the class name combined with the pacakge name in order
        to form a normal name for a table in SQL.
        """
        package = _package_of(cls.__module__).lower()
        name = '%s.%s' % (package, cls.__name__.lower())
        name = re.sub(r'([A-Z])', r'_\1', name)
        name = re.sub(r'\.+', r'_', name)
        return name

    def save(self, session=None, commit=True):
        """
        Save the changes to the model. If the model has not been persisted
        then it adds the model to the declared session. Then it flushes the
        object session and optionally commits it.

        @param[in] session
            A specific session to use instead of the thread-local, scoped
            session.
        """
        if has_identity(self):
            # Object has already been persisted to the database; grab its
            # session.
            session = object_session(self)

        else:
            # Ensure we have a database session.
            if session is None:
                session = __import__('alchemist.db').db.session

            # Object has not been persisted to the database.
            session.add(self)

        if commit:
            # Commit the session as requested.
            session.commit()

        else:
            # Just flush the session; do not commit.
            session.flush()
