# -*- coding: utf-8 -*-
from alchemist import management
from flask import Flask


class TestManager:

    def setup(self):
        self.app = Flask('alchemist')
        self.app.config['COMPONENTS'] = ['alchemist']

    def test_discover_commands(self):
        """Should discover commands from registered components.
        """

        manager = management.Manager(self.app)

        assert 'runserver' in manager._commands
