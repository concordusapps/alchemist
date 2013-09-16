# -*- coding: utf-8 -*-
import flask
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
            return flask.current_app.config[name]

        except RuntimeError:
            raise KeyError

    def __contains__(self, name):
        try:
            return name in flask.current_app.config

        except RuntimeError:
            return False

    def __len__(self):
        try:
            return len(flask.current_app.config)

        except RuntimeError:
            return 0

    def __iter__(self):
        try:
            return iter(flask.current_app.config)

        except:
            return iter(())

# Instantiate lazy-bound settings object.
settings = Settings()
