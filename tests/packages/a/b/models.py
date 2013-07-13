# -*- coding: utf-8 -*-
import sqlalchemy as sa
from alchemist.db import models


class BBlock(models.Model):

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)


class BWall(models.Model):

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
