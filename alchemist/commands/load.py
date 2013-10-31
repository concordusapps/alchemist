# -*- coding: utf-8 -*-
import os
from collections import defaultdict
from flask.ext.script import Command, Option
from alchemist import db
from alchemist.db.model import _component_of
from pkgutil import get_importer
from termcolor import colored
from sqlalchemy import event
from six import print_
from sqlalchemy.orm import Mapper


class Load(Command):
    """Loads the passed named fixture or file.
    """

    name = 'load'

    # The idea is to eventually extend this command to support:

    # @code
    # $ alchemist load <file.(json|yml|py)> [--database <database>]
    # $ alchemist load <name> [--database <database>]
    # @endcode

    # Where the second form would traverse each package and look for a
    # <name>.(json|yml|py) in the package or in a fixtures folder of the
    # package and load each one.

    option_list = [Option(dest='filename')]

    def run(self, filename):
        # Resolve the absoulte path.
        path = os.path.abspath(filename)

        # Resolve the module name.
        name = os.path.basename(os.path.splitext(path)[0])

        # Create a after_* hook so that we can record what happens.
        models = defaultdict(int)

        @event.listens_for(Mapper, 'after_insert')
        def hook(mapper, connection, target):
            target_cls = type(target)
            component = _component_of(target_cls.__module__)
            name = '%s.%s' % (component, target_cls.__name__)
            models[name] += 1

        try:
            # Import and execute the file.
            imp = get_importer(os.path.dirname(filename))
            imp.find_module(name).load_module(name)

            # Commit the session.
            db.session.commit()

        except:
            # Something happened; rollback the session.
            db.session.rollback()

            # Re-raise so the console gets the traceback.
            raise

        # Get sizes for logging.
        max_count = len(str(max(models.values())))

        # Let the user know.
        for name, count in models.items():
            msg = ('{:>%s} {}' % (max_count)).format(count, name)
            print_(colored(' *', 'white', attrs=['dark']),
                   colored('insert', 'cyan'),
                   colored(msg, 'white'),
                   colored('default', 'white', attrs=['dark']))
