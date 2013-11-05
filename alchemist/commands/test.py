# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext.script import Command, Option
from alchemist import app
import pytest
from os import path
from importlib import import_module


class Test(Command):

    name = 'test'

    option_list = [
        Option(dest='name', nargs='?',
               help='The name of the component (or project) to test.'),
    ]

    capture_all_args = True

    def run(self, *args, **kwargs):

        # Use the project (package) name if no name was provided.
        # This would execute tests at '<project>/tests'.

        name = kwargs.pop('name') or app.application.name
        application = app._get_application_from_name(name)

        # Get the test directory.

        module = import_module(name)
        directory = path.join(path.dirname(module.__file__), 'tests')
        if not path.exists(directory):
            directory += '.py'

        # Execute 'py.test' with the remaining arguments.

        pytest.main([directory] + list(*args))
