from armet.connectors.flask import resources as flask_resources
from armet.connectors.sqlalchemy import resources as sqlalchemy_resources

__all__ = [
    'Resource',
    'ModelResource',
    'ModelResourceOptions'
]


class Resource(flask_resources.Resource):
    pass


class ModelResourceOptions(sqlalchemy_resources.ModelResourceOptions):
    pass


class ModelResource(sqlalchemy_resources.ModelResource):
    pass
