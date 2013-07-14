# -*- coding: utf-8 -*-
from flask import Flask
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

# Export named attributes.
__all__ = [
    'application'
]

# Create a new flask application context.
application = Flask(__name__)

# Configure the application.
application.config['DATABASES'] = {'default': 'sqlite:///:memory:'}

# Create a sqlalchemy base.
Base = declarative_base()


class Wall(Base):

    __tablename__ = 'wall'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)


class Block(Base):

    __tablename__ = 'block'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
