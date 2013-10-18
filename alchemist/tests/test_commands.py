# -*- coding: utf-8 -*-
from alchemist import management, test
from flask import Flask
from unittest import mock
import sys


class TestServer:

    def setup(self):
        self.app = Flask('alchemist')
        self.app.config['COMPONENTS'] = ['alchemist']

    def _run(self, command, patch='flask.ext.script.Server.handle'):
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
