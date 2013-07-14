# -*- coding: utf-8 -*-
from os import path
from alchemist.conf import settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = path.abspath(path.join(path.dirname(__file__), '..', '..'))

# List of registered packages.
# These packages are considered for all database and fixture commands.
PACKAGES = settings['PACKAGES'] + [
    'a.b',
]

# Database configuration.
DATABASES = {
    'default': {
        'engine': 'sqlite',
        'name': 'a.sqlite3'
    },

    'other': 'sqlite:///db.sqlite3'
}
