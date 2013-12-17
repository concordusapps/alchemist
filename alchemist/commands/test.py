# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext.script import Command, Option
import pytest
from os import path
from alchemist import app
from alchemist.conf import settings
from importlib import import_module


class Test(Command):

    name = 'test'

    option_list = [
        Option(dest='names', nargs='*',
               help='The name of the component (or project) to test.'),
    ]

    capture_all_args = True

    def run(self, *args, **kwargs):

        collected = []
        names = kwargs.pop('names')
        default_names = {app.application.name} | set(settings['COMPONENTS'])
        for name in (names or default_names):

            # Get the tests module or package location.

            module = import_module(name)
            tests = path.join(path.dirname(module.__file__), 'tests')
            if not path.exists(tests):
                tests += '.py'
                if not path.exists(tests):
                    continue

            # Collect all test components that are not alchemist.

            if name != 'alchemist':
                collected.append(tests)

        # Run collected test modules.
        pytest.main(collected + list(*args))
