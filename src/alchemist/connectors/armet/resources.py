from armet.connectors.flask import resources as flask_resources
from armet.connectors.sqlalchemy import resources as sqlalchemy_resources
from armet import utils
from alchemist import db
import warnings

__all__ = [
    'Resource',
    'ModelResource',
]


class Resource(flask_resources.Resource):

    @property
    def session(self):
        return db.session

    def route(self, *args, **kwargs):
        try:
            # Continue on with the cycle.
            result = utils.super(Resource, self).route(*args, **kwargs)

            # Commit the session.
            db.commit()

            # Return the result.
            return result

        except:
            # Something occurred; rollback the session.
            db.rollback()

            # Re-raise the exception.
            raise


class ModelResource(sqlalchemy_resources.ModelResource):

    def route(self, *args, **kwargs):
        return utils.super(sqlalchemy_resources.ModelResource, self).route(
            *args, **kwargs)
