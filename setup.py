#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
from imp import load_source
import sys

test_requirements = []
if sys.version_info[0] < 3:
    test_requirements += ['mock']


setup(
    name='alchemist',
    version=load_source('', 'alchemist/_version.py').__version__,
    description='A server architecture built on top of a solid foundation '
                'provided by flask, sqlalchemy, and various extensions.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        # 'Framework :: SQLAlchemy',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/concordusapps/alchemist',
    packages=[
        'alchemist',
        'alchemist.commands',
        'alchemist.db'
    ],
    # entry_points={'pytest11': ['alchemist = alchemist.plugin']},
    dependency_links=[
        # wsgi_intercept
        # <https://code.google.com/p/wsgi-intercept/issues/detail?id=25>
        # 'git+git://github.com/concordusapps/wsgi-intercept.git'
        # '#egg=wsgi_intercept-0.6.0',

        'git+git://github.com/concordusapps/flask-script.git@edge#egg=flask-script-edge',
        'https://launchpad.net/oursql/py3k/py3k-0.9.4/+download/oursql-0.9.4.tar.gz#egg=oursql-0.9.4'
    ],
    install_requires=[
        'colorama',
        'termcolor >= 1.1, < 1.2',
        'flask >= 0.10',
        'blinker >= 1.3',
        'flask-script == edge',
        'flask-components >= 0.1',
        'sqlalchemy >= 0.8',
        'sqlalchemy-utils >= 0.16',
        'alembic >= 0.6, < 0.7',
        'pytest >= 2.4',
        'pytest-pep8 >= 1.0',
        'pytest-cov >= 1.6',
        'pygments'
    ],
    tests_require=test_requirements,
    extras_require={
        'test': test_requirements,
        'mysql': ['oursql >= 0.9.4']
    }
)
