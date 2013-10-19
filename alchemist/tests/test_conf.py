# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from flask import Flask
import pytest
from alchemist.conf import settings


class TestSettings:

    def test_no_context(self):
        with pytest.raises(KeyError):
            settings['COMPONENTS']

        assert settings.get('COMPONENTS') is None
        assert 'COMPONENTS' not in settings
        assert len(settings) == 0
        assert len(list(iter(settings))) == 0

    def test_with_context(self):
        app = Flask('alchemist')
        app.config['A_SETTING'] = 1
        with app.app_context():
            assert 'A_SETTING' in settings
            assert settings['A_SETTING'] == 1
            assert len(settings) > 0
            assert len(list(iter(settings))) > 0
