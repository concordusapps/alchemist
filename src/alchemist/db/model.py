# -*- coding: utf-8 -*-
from alchemist import db, utils
from alchemist.db.query import Query
from sqlalchemy.ext.declarative import declared_attr, declarative_base, DeclarativeMeta, base
import sqlalchemy as sa
import weakref


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
        package.pop()

    if not package and '.models' in name:
        # No package was found to be registered; attempt to guess the
        # right package name; strip all occurrances of '.models' from the
        # pacakge name.
        return name.replace('.models', '')


#! Project-wide model metadata.
_metadata = sa.Metadata()


#! Project-wide declarative class registry.
_registry = weakref.WeakValueDictionary()


class ModelBase(DeclarativeMeta):
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
            from alchemist import db
            db.session.query(Model).all()
        """

        return db.session.query(self)

    @property
    def _decl_class_registry(self):
        return getattr(self.__registry, None)

    def __new__(cls, name, bases, attrs):

        # Don't process further if this is the base.

        if not any(lambda x: isinstance(x, ModelBase), bases):

            # This is the base class; skip.

            return super(ModelBase, cls).__new__(cls, name, bases, attrs)

        # Check if this model is in a registered component and set its
        # declarative registry and metadata to share the global if so; else,
        # generate its own.

        attrs['_component'] =  component = _component_of(attrs['__module__'])
        if component:
            attrs['_ModelBase__registry'] = _registry
            attrs['metadata'] = _metadata

        else:
            attrs['_ModelBase__registry'] = weakref.WeakValueDictionary()
            attrs['metadata'] = sa.Metadata()


class Model(six.with_metaclass(ModelBase)):

    __abstract__ = True
