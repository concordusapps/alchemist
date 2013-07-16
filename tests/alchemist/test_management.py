# -*- coding: utf-8 -*-
import sys
import re
import os
import io
from alchemist import management
import py


def strip_colors(text):
    return re.sub("\x1b\[\d+m", "", text)


class BaseTest:

    def setup(self):
        # Unload all alchemist.* modules and test packages.
        for name in list(sys.modules.keys()):
            for test in ['a', 'a.b', 'a.b.c', 'example', 'alchemist']:
                if name.startswith(test) and name in sys.modules:
                    del sys.modules[name]


class TestDiscover:

    def setup(self):
        self.cwd = os.getcwd()
        self.base = os.path.join(os.path.dirname(__file__), '..')

    def teardown(self):
        os.chdir(self.cwd)

    def test_same_level(self):
        os.chdir(os.path.join(self.base, 'packages'))

        application = management.discover()

        assert application is not None
        assert application.name == 'a'

    def test_nested(self):
        os.chdir(os.path.join(self.base, 'discover', 'nested'))

        application = management.discover()

        assert application is not None
        assert application.name == 'a'

    def test_nested_too_low(self):
        os.chdir(os.path.join(self.base, 'discover'))

        application = management.discover()

        assert application is None

    def test_basic(self):
        os.chdir(os.path.join(self.base, 'discover', 'basic', 'src'))

        application = management.discover()

        assert application is not None
        assert application.name == 'basic'

    def test_up_one_level(self):
        os.chdir(os.path.join(self.base, 'packages', 'a'))

        application = management.discover()

        assert application is not None
        assert application.name == 'a'

    def test_up_two_levels(self):
        os.chdir(os.path.join(self.base, 'packages', 'a', 'b'))

        application = management.discover()

        assert application is not None
        assert application.name == 'a'

    def test_up_three_levels(self):
        os.chdir(os.path.join(self.base, 'packages', 'a', 'b', 'c'))

        application = management.discover()

        assert application is not None
        assert application.name == 'a'


class TestCommand(BaseTest):

    def setup(self):
        self.argv = sys.argv
        self.cwd = os.getcwd()
        self.base = os.path.join(os.path.dirname(__file__), '..')

    def teardown(self):
        sys.argv = self.argv
        os.chdir(self.cwd)

    def test_show_nested(self):
        os.chdir(os.path.join(self.base, 'packages', 'a'))

        capture = py.io.StdCaptureFD()
        management.run(['show'])

        out, _ = capture.done()

        assert out.read() == "<Alchemist 'a'>\n"

    def test_run_show(self):
        os.chdir(os.path.join(self.base, 'packages', 'a'))
        sys.argv = ['alchemist', 'show']

        # Prevent exit.
        exit = sys.exit
        sys.exit = lambda status: status

        capture = py.io.StdCaptureFD()
        management.Manager().run()

        out, _ = capture.done()

        assert out.read() == "<Alchemist 'a'>\n"

        # Undo exit prevention.
        sys.exit = exit

    def test_db_init_nested(self):
        os.chdir(os.path.join(self.base, 'packages', 'a'))

        capture = py.io.StdCaptureFD()
        management.run(['db', 'init'])

        out, err = capture.done()

        text = strip_colors(err.read())
        lines = [x.strip() for x in text.split('\n')]

        assert lines[0] == 'alchemist db init a'
        assert lines[3] == 'alchemist db init a.b'

    def test_db_init_nested_name(self):
        os.chdir(os.path.join(self.base, 'packages', 'a'))

        capture = py.io.StdCaptureFD()
        management.run(['db', 'init', 'a'])

        out, err = capture.done()

        text = strip_colors(err.read())
        lines = [x.strip() for x in text.split('\n')]

        assert lines[0] == 'alchemist db init a'
        assert len(lines) == 4

    def test_db_clear_nested(self):
        os.chdir(os.path.join(self.base, 'packages', 'a'))

        capture = py.io.StdCaptureFD()
        management.run(['db', 'clear'])

        out, err = capture.done()

        text = strip_colors(err.read())
        lines = [x.strip() for x in text.split('\n')]

        assert lines[0] == 'alchemist db clear a.b'
        assert lines[1] == 'alchemist db clear a'

    def test_db_flush_nested(self):
        os.chdir(os.path.join(self.base, 'packages', 'a'))

        capture = py.io.StdCaptureFD()
        management.run(['db', 'flush'])

        out, err = capture.done()

        text = strip_colors(err.read())
        lines = [x.strip() for x in text.split('\n')]

        assert lines[0] == 'alchemist db flush a.b'
        assert lines[1] == 'alchemist db flush a'

    def test_shell_context(self):
        os.chdir(os.path.join(self.base, 'packages', 'a'))

        application = management.discover()
        with application.app_context():
            from alchemist.commands import shell
            from a import models

            context = shell._make_context(quiet=True)

            assert 'session' in context
            assert 'db' in context
            assert 'ABlock' in context
            assert context['ABlock'] == models.ABlock
