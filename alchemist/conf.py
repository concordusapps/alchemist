# -*- coding: utf-8 -*-
from alchemist import app
import collections

__all__ = [
    'settings'
]


class Settings(collections.Mapping):
    """
    A proxy dictionary-like object that proxies to the current app
    configuration; or, if not in an active application context, pretends
    to be an empty dictionary.
    """

    def __getattr__(self, name):
        try:
            return self[name]

        except KeyError:
            raise AttributeError

    def __getitem__(self, name):
        try:
            return app.application.config[name]

        except (AttributeError, RuntimeError):
            raise KeyError

    def __contains__(self, name):
        try:
            return name in app.application.config

        except (AttributeError, RuntimeError):
            return False

    def __len__(self):
        try:
            return len(app.application.config)

        except (AttributeError, RuntimeError):
            return 0

    def __iter__(self):
        try:
            return iter(app.application.config)

        except:
            return iter(())


# Instantiate lazy-bound settings object.
settings = Settings()
