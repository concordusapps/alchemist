# -*- coding: utf-8 -*-
import sqlalchemy as sa
from alchemist.db import models


class ExampleBlock(models.Model):

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)


class ExampleWall(models.Model):

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
