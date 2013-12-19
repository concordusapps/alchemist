# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from alchemist.db import session
from alchemist.conf import settings
from importlib import import_module
from alchemist.db.query import Query
from sqlalchemy.orm.util import has_identity
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta, base
import sqlalchemy as sa
import weakref
import re
import six


def _component_of(name):
    """Get the root package or module of the passed module.
    """

    # Get the registered package this model belongs to.
    segments = name.split('.')
    while segments:
        # Is this name a registered package?
        test = '.'.join(segments)
        if test in settings.get('COMPONENTS', []):
            # This is the component we are in.
            return test

        # Remove the right-most segment.
        segments.pop()

    if not segments and '.models' in name:
        # No package was found to be registered; attempt to guess the
        # right package name; strip all occurrances of '.models' from the
        # pacakge name.
        return _component_of(name.replace('.models', ''))


#! Global model metadata.
_metadata = sa.MetaData()

#! Componentized model metadata.
_metadata_map = {}

#! Componentized declarative class registries.
_registry_map = {}


def _is_model(name, bases, attrs):

    if name == 'NewBase' and not attrs and not bases:

        # Six contrivance; ensure we skip it.

        attrs['__abstract__'] = True
        return False

    for base in bases:

        if (base.__module__.startswith('alchemist.db.model')
                and base.__name__ == 'NewBase'):

            # This is an internal utility to alchemist.

            continue

        if isinstance(base, ModelBase):

            # This is at least dervied at some point from Model.

            return True

    # This is the base class, Model.

    return False


class ModelBaseProxy(type):

    def __new__(cls, name, bases, attrs):
        # Resolve the metaclass we should be derived from.
        meta_name = settings['MODEL_METACLASS']
        segs = meta_name.split('.')
        meta = getattr(import_module('.'.join(segs[:-1])), segs[-1])

        if not issubclass(bases[0], meta):
            bases = meta,

        return super(ModelBaseProxy, cls).__new__(cls, name, bases, attrs)


class ModelBase(six.with_metaclass(ModelBaseProxy, type)):
    """The metaclass for user-defined models.

    The basic concept is as follows: every model declared in a registered
    component shares the same underlying declarative base. Every model
    declared outside a registered component gets its own declarative base.

    A model is considered declared inside a component whether that be directly
    or nested in a sub-package.
    """

    #! The query class used. The query property returns an instance of this
    #! class.
    __query__ = Query

    #! The component this model belongs to.
    _component = None

    #! A reference to the declarative class registry if the model is
    #! in a registered component.
    __registry = None

    @property
    def query(self):
        """
        Create a session query over this model. ::
            Model.query.all()

        Equivalent to ::
            from alchemist.db import session
            session.query(Model).all()
        """

        return session.query(self)

    @property
    def _decl_class_registry(self):
        return getattr(self, '_ModelBase__registry', None)

    def __new__(cls, name, bases, attrs):

        # Don't process further if this is not a model (ie. the base class).

        if not _is_model(name, bases, attrs):

            return super(ModelBase, cls).__new__(cls, name, bases, attrs)

        # Check if this model is in a registered component and set its
        # declarative registry and metadata to share the global if so; else,
        # generate its own.

        attrs['_component'] = component = _component_of(attrs['__module__'])

        if component:
            if component not in _registry_map:
                _registry_map[component] = weakref.WeakValueDictionary()

            attrs['_ModelBase__registry'] = _registry_map[component]
            attrs['metadata'] = _metadata

        else:
            attrs['_ModelBase__registry'] = weakref.WeakValueDictionary()
            attrs['metadata'] = sa.MetaData()

        return super(ModelBase, cls).__new__(cls, name, bases, attrs)

    def __init__(self, name, bases, attrs):
        # Initialize ourself.
        super(ModelBase, self).__init__(name, bases, attrs)

        # Just short-circuit if we're that six contraption, NewBase.
        if self.__module__ == 'alchemist.db.model' and name == 'NewBase':
            return

        abstract = attrs.get('__abstract__', False)
        if _is_model(name, bases, attrs) and not abstract:

            # Add a reference to the model on the table.

            table = self.__table__
            setattr(table, 'class_', weakref.proxy(self))

            # Add ourself to the componetized metadata.

            if self._component:
                if self._component not in _metadata_map:
                    _metadata_map[self._component] = sa.MetaData()

                _metadata_map[self._component]._add_table(
                    table.name,
                    _metadata.tables[table.name].schema or _metadata.schema,
                    table)


class Model(six.with_metaclass(ModelBase)):

    __abstract__ = True

    __init__ = base._declarative_constructor

    @declared_attr
    def __tablename__(cls):
        """
        Underscorizes the class name combined with the pacakge name in order
        to form a normal name for a table in SQL.
        """
        component = cls._component
        name = '%s.%s' % (component, cls.__name__.lower())
        name = re.sub(r'([A-Z])', r'_\1', name)
        name = re.sub(r'\.+', r'_', name)
        return name

    def save(self, commit=False):
        """Save the changes to the model.

        If the model has not been persisted
        then it adds the model to the declared session. Then it flushes the
        object session and optionally commits it.
        """
        if not has_identity(self):
            # Object has not been persisted to the database.
            session.add(self)

        if commit:
            # Commit the session as requested.
            session.commit()

        else:
            # Just flush the session; do not commit.
            session.flush()
