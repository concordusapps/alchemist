# -*- coding: utf-8 -*-
from flask import Flask
import sqlalchemy as sa
from alchemist.db import models

# Export named attributes.
__all__ = [
    'application'
]

# Create a new flask application context.
application = Flask(__name__)

# Configure the application.
application.config['DATABASES'] = {'default': 'sqlite:///:memory:'}


class Wall(models.Model):

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)


class Block(models.Model):

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
