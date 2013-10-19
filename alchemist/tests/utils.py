# -*- coding: utf-8 -*-
import sys


def unload_modules(name):
    """Unload all modules where the name begins with the passed name.
    """

    for key in list(sys.modules.keys()):

        if key.startswith(name):

            del sys.modules[key]
