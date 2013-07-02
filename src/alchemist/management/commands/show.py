# -*- coding: utf-8 -*-
import flask
from flask.ext.script import Command


class Show(Command):
    """Show the name and package of the application.
    """

    #! Name of the command as it is invoked on the command line.
    name = 'show'

    def run(self):
        print(flask.current_app)
