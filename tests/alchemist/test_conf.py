# -*- coding: utf-8 -*-
import pytest
from alchemist.conf import settings


class TestSettings:

    def test_no_context(self):
        with pytest.raises(KeyError):
            settings['PACKAGES']

        assert settings.get('PACKAGES') is None
        assert 'PACKAGES' not in settings
        assert len(settings) == 0
        assert len(list(iter(settings))) == 0

    def test_with_context(self):
        from a import application
        with application.app_context():
            assert 'a.b' in settings['PACKAGES']
            assert settings['PACKAGES'][-1] == 'a.b'
            assert len(settings) > 0
            assert len(list(iter(settings))) > 0
