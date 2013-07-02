# -*- coding: utf-8 -*-
from datetime import datetime
import sqlalchemy as sa


class Timestamp:
    """Records when a model has been created and updated.
    """

    created = sa.Column(
        sa.DateTime, default=datetime.utcnow, nullable=False,
        doc='Date and time the model was created.')

    updated = sa.Column(
        sa.DateTime, default=datetime.utcnow, nullable=False,
        doc='Date and time the model was last updated.')


@sa.event.listens_for(Timestamp, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    # When a model with a timestamp is updated; force update the updated
    # timestamp.
    target.updated = datetime.utcnow()
