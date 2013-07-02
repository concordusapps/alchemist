# -*- coding: utf-8 -*-
import pytest
from alchemist.db import Session
from alchemist.conf import settings
from alchemist.management.commands import db


class TestModelBase:

    #! List of packages used during testing; limits the number of packages
    #! that are reset after each test run.
    #! Default: reset all packages.
    packages = None

    @pytest.fixture(autouse=True, scope='class')
    def database(cls, request):
        # Initialize the database access layer.
        db.init(names=cls.packages)

        # TODO: Load any required fixtures.

    @classmethod
    def setup_class(cls):
        # Instantiate a session to the database.
        cls.session = Session()

        # Create a shortcut for querying because we're all lazy and we
        # know it.
        cls.Q = lambda s, x: cls.session.query(x)

    def teardown(self):
        # Flush the database access layer.
        db.flush(names=self.packages)

        # TODO: Re-load any desired fixtures.
