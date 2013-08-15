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

        # Save a copy of the thread-local stored session so that we can
        # restore it after this request completes.
        local_session = db._local.instance

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

            # Restore the thread-local session.
            db._local.instance = local_session


class ModelResource(sqlalchemy_resources.ModelResource):
    pass
