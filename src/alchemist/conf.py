# -*- coding: utf-8 -*-
import flask
import collections


class Settings(collections.Mapping):

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
