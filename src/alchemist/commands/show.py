# -*- coding: utf-8 -*-
from flask.ext.script import Command


class Show(Command):
    """Show the name and package of the application.
    """

    def run(self):
        print(__import__('alchemist').application)
