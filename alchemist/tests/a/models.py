import sqlalchemy as sa
from alchemist import db


class Entity(db.Model):

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)


class Box(db.Model):

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
