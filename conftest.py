# -*- coding: utf-8 -*-
import sys
from os import path

# Append the source and test packages directories to PATH.
sys.path.append(path.join(path.dirname(__file__), 'src'))
sys.path.append(path.join(path.dirname(__file__), 'tests', 'packages'))
