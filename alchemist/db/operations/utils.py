# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from six import print_
from termcolor import colored
import sys


def is_table_included(table, names):
    """Determines if the table is included by reference in the names.
    """

    # No names indicates that every table is included.

    if not names:
        return True

    # Introspect the table and pull out the model and component from it.

    model, component = table.class_, table.class_._component

    # Check for the component name.

    if component in names:
        return True

    # Check for the full python name.

    model_name = '%s.%s' % (model.__module__, model.__name__)

    if model_name in names:
        return True

    # Check for the short name.

    short_name = '%s:%s' % (component, model.__name__)

    if short_name in names:
        return True

    return False


def print_command(indicator, name, target, extra):
    print_(colored(indicator, 'white', attrs=['dark']),
           colored(name, 'cyan'),
           colored(target, 'white'),
           colored(extra, 'white', attrs=['dark']),
           file=sys.stderr)
