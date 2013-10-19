import sqlalchemy as sa
from alchemist import db
from ..models import Entity


class Box(db.Model):

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)


class Plane(Entity):

    id = sa.Column(sa.Integer, sa.ForeignKey(Entity.id), primary_key=True)
