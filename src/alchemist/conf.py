# -*- coding: utf-8 -*-
import flask
import collections


class Settings(collections.Mapping):

    def __getitem__(self, name):
        return flask.current_app.config[name]

    def __contains__(self, name):
        return name in flask.current_app.config

    def __len__(self):
        return len(flask.current_app.config)

    def __iter__(self):
        return iter(flask.current_app.config)


# Instantiate lazy-bound settings object.
settings = Settings()
