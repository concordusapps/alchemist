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

    # The idea is to eventually extend this command to support:

    # @code
    # $ alchemist load <file.(json|yml|py)>
    # $ alchemist load <name>
    # @endcode

    # Where the second form would traverse each package and look for a
    # <name>.(json|yml|py) in the package or in a fixtures folder of the
    # package and load each one.

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
