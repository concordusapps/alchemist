# -*- coding: utf-8 -*-
from alchemist import Alchemist

# Create a new alchemist application context.
application = Alchemist(__package__)

# Export named attributes.
__all__ = [
    'application'
]
