# -*- coding: utf-8 -*-
import os
from flask.ext.script import Command, Option
from alchemist import db
from termcolor import colored


class Load(Command):
    """
    Loads the passed file, executes it, and commits the scoped
    session afterwards.
    """

    #! Name of the command as it is invoked on the command line.
    name = 'load'

    option_list = Option(dest='filename'),

    def run(self, filename):
        # Load and execute the file.
        with open(filename) as stream:
            exec(stream.read())

        # Let the user know.
        print(colored('alchemist', 'grey'),
              colored('load', 'cyan'),
              '{} objects'.format(len(db.session.new)),
              colored(os.path.abspath(filename), 'grey'))

        # Commit the session.
        db.session.commit()
