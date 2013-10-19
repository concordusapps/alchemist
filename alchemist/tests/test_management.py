# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
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

        assert 'run' in manager._commands
