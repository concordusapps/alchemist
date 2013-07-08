# -*- coding: utf-8 -*-
import os
import sys
import pytest
from alchemist.conf import settings
from flask.ext.script import Command


class Test(Command):
    """Runs py.test programmatically at the right place.
    """

    #! Name of the command as it is invoked on the command line.
    name = 'test'

    capture_all_args = True

    def run(self, *args, **kwargs):
        # Use the app directory setting and run the test suite back one
        # directory.
        directory = os.path.join(settings['APP_DIR'], '..')
        os.chdir(directory)

        # Remove our name from the command-line.
        del sys.argv[1]

        # Run pytest interactively.
        pytest.main()
