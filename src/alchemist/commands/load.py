# -*- coding: utf-8 -*-
import os
from flask.ext.script import Command, Option
from alchemist import db
from .utils import print_command


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

    option_list = [Option(dest='filename')]

    def run(self, filename):
        # Load and execute the file.
        with open(filename) as stream:
            exec(stream.read())

        # Let the user know.
        print_command('alchemist', 'load', '%s objects' % len(db.session.new),
                      os.path.abspath(filename))

        # Commit the session.
        db.session.commit()
