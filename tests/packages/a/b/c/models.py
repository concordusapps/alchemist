# -*- coding: utf-8 -*-
import sqlalchemy as sa
from alchemist.db import models


class CBlock(models.Model):

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)


class CWall(models.Model):

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
