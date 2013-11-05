# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask.ext.script import Command, Option
from alchemist import app, utils
from alchemist.app import _get_application_from_name as _get_app
import pytest
from os import path
from alchemist.conf import settings
from importlib import import_module
from subprocess import Popen


class Test(Command):

    name = 'test'

    option_list = [
        Option(dest='names', nargs='*',
               help='The name of the component (or project) to test.'),
    ]

    capture_all_args = True

    def run(self, *args, **kwargs):

        names = kwargs.pop('names')
        for name in (names or settings['COMPONENTS']):

            # Get the tests module or package location.

            module = import_module(name)
            tests = path.join(path.dirname(module.__file__), 'tests')
            if not path.exists(tests):
                tests += '.py'
                if not path.exists(tests):
                    continue

            # Indicate progress.

            utils.print_('*', 'test', name, path.relpath(path.abspath(tests)))

            # Decide on command and arguments.
            # Alchemist should not use its own plugin.

            if name == 'alchemist':
                command = ['py.test', '-p', 'no:alchemist']

            else:
                command = ['py.test']

            # Pre-function is needed to create the app context.

            if name != 'alchemist':
                def pre(name=name):
                    application = _get_app(name)
                    application.app_context().push()

            else:
                pre = lambda: None

            # Execute 'py.test' with the remaining arguments.

            cwd = path.dirname(tests)
            tests = path.relpath(tests, cwd)
            command += [tests] + list(*args)
            process = Popen(command, cwd=cwd, preexec_fn=pre)
            process.wait()
