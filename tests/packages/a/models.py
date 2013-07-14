# -*- coding: utf-8 -*-
import sqlalchemy as sa
from alchemist.db import models, query


class ABlockQuery(query.Query):

    def flail(self):
        raise RuntimeError('Flail')


class ABlock(models.Model):

    __query__ = ABlockQuery

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)


class AWall(models.Model):

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
