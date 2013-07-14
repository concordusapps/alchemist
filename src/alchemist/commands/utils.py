# -*- coding: utf-8 -*-
import sys
from termcolor import colored

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
