#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from imp import load_source
import sys


test_requirements = [
    'pytest >= 2.4',
    'pytest-pep8 >= 1.0',
    'pytest-cov >= 1.6'
]

if sys.version_info[0] < 3:
    test_requirements += ['mock']
    mysql_requirements = ['oursql == 0.9.3']

else:
    mysql_requirements = ['oursql == 0.9.4']


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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/concordusapps/alchemist',
    packages=find_packages('.'),
    entry_points={'pytest11': ['alchemist = alchemist.plugin']},
    dependency_links=[
        'https://launchpad.net/oursql/py3k/py3k-0.9.4/+download/'
        'oursql-0.9.4.tar.gz#egg=oursql-0.9.4',

        'git+git://github.com/kvesteri/sqlalchemy-utils.git'
        '#egg=sqlalchemy-utils-0.21.0',
    ],
    install_requires=[
        'colorama',
        'termcolor >= 1.1, < 1.2',
        'flask >= 0.10',
        'blinker >= 1.3',
        'flask-components >= 0.1',
        'flask-script >= 0.6.6',
        'sqlalchemy >= 0.8',
        'sqlalchemy-utils >= 0.21',
        'alembic >= 0.6, < 0.7',
        'pygments',
        'requests',
        'wsgi_intercept >= 0.6.0'
    ] + test_requirements,
    tests_require=test_requirements,
    extras_require={
        'mysql': mysql_requirements
    }
)
