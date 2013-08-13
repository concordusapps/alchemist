from armet.connectors.flask import resources as flask_resources
from armet.connectors.sqlalchemy import resources as sqlalchemy_resources
from armet import utils
from alchemist import db

__all__ = [
    'Resource',
    'ResourceOptions',
    'ModelResource',
]


class ResourceOptions(object):

    def __init__(self, meta, name, bases):
        #! SQLAlchemy session used to perform operations on the models.
        self.Session = meta.get('Session')
        if not self.Session:
            # Default this to an alchemist-provided session.
            self.Session = db.Session


class Resource(flask_resources.Resource):

    def route(self, *args, **kwargs):
        # Establish a session.
        self.session = session = db.Session()

        # Bind the session to the thread-local store.
        db._local.instance = self.session

        try:
            # Continue on with the cycle.
            result = utils.super(Resource, self).route(*args, **kwargs)

            # Commit the session.
            session.commit()

            # Return the result.
            return result

        except:
            # Something occurred; rollback the session.
            session.rollback()

            # Re-raise the exception.
            raise

        finally:
            # Close the session.
            session.close()

            # Revoke the thread-local session.
            del db._local.instance


class ModelResource(sqlalchemy_resources.ModelResource):
    pass
