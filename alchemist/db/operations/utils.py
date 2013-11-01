# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from pygments.formatters import TerminalFormatter
from pygments.lexers import SqlLexer
import pygments
import sys


def highlight(text):
    if sys.stdout.isatty():  # pragma: nocoverage
        return pygments.highlight(text, SqlLexer(), TerminalFormatter())

    return text


class HighlightStream(object):

    def __init__(self, stream):
        self.stream = stream

    def write(self, chunk):
        self.stream.write(highlight(chunk))
