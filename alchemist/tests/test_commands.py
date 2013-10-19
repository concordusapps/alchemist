# -*- coding: utf-8 -*-
from alchemist import test
import alchemist
from flask import Flask
from unittest import mock
import sys
import io
import py
from . import utils


class CommandTest:

    def setup(self):
        self.app = Flask('alchemist')
        self.app.config['COMPONENTS'] = ['alchemist']

    def _run(self, command, patch=None):
        from alchemist import management

        if patch is None:
            patch = self.patch

        target = mock.MagicMock()
        with mock.patch(patch, target):
            manager = management.Manager(self.app)

            _argv = sys.argv
            sys.argv = ['alchemist'] + command
            try:
                manager.run()

            except SystemExit:
                return target

            finally:
                sys.argv = _argv


class TestServer(CommandTest):

    patch = 'flask.ext.script.Server.handle'

    def test_default(self):
        target = self._run(['run'])
        target.assert_called_with(
            self.app, host='::1', port=8000, use_debugger=True,
            threaded=False, processes=1,
            passthrough_errors=False, use_reloader=True)

    def test_override(self):
        config = {
            'SERVER_HOST': 'app.me',
            'SERVER_PORT': 5000,
            'SERVER_RELOAD': False,
            'SERVER_PROCESSES': 10,
            'SERVER_THREADED': True,
            'SERVER_DEBUG': False
        }

        with test.settings(self.app, **config):
            target = self._run(['run'])
            target.assert_called_with(
                self.app, passthrough_errors=False,
                host=config['SERVER_HOST'],
                port=config['SERVER_PORT'],
                use_reloader=config['SERVER_RELOAD'],
                use_debugger=config['SERVER_DEBUG'],
                processes=config['SERVER_PROCESSES'],
                threaded=config['SERVER_THREADED'])


class TestShell(CommandTest):

    patch = 'flask.ext.script.Shell.run'

    def test_run(self):
        target = self._run(['shell'])
        target.assert_called()

    def test_context(self):
        utils.unload_modules('alchemist')

        from alchemist.commands import Shell
        shell = Shell()

        self.app = Flask('alchemist.tests.a')
        self.context = self.app.app_context()
        with self.context:

            alchemist.configure(self.app)

            context = shell.make_context()

            assert 'db' in context
            assert 'session' in context
            assert 'Entity' in context

    def test_pipe(self):
        utils.unload_modules('alchemist')

        self.app = Flask('alchemist.tests.a')
        self.context = self.app.app_context()

        with self.context:
            alchemist.configure(self.app)

            stdin = sys.stdin
            sys.stdin = io.StringIO('print(Entity)\nprint(session)')

            capture = py.io.StdCapture(out=True, in_=False)
            self._run(['shell', '--pipe'])
            out, err = capture.done()

            text = ("<class 'alchemist.tests.a.models.Entity'>\n"
                    "<Session(bind=Engine(sqlite:///:memory:))>\n")

            assert text == out.read()

            sys.stdin = stdin
