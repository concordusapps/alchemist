# -*- coding: utf-8 -*-
import collections
import sys
import contextlib
from importlib import import_module
import sqlalchemy as sa
from sqlalchemy import schema
from sqlalchemy.orm.query import Query
from flask.ext import script
from termcolor import colored
from alchemist import application
from alchemist.conf import settings

# Alias some colors.
colored_info = lambda x: colored(x, 'white', attrs=['dark'])
colored_command = lambda x: colored(x, 'cyan')
colored_name = lambda x: colored(x, 'white')

def print_command(info, command, name, *more):
    print(colored_info(info),
          colored_command(command),
          colored_name(name),
          colored_info(' '.join(more)),
          file=sys.stderr)
