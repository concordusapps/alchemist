#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from imp import load_source


setup(
    name='alchemist',
    version=load_source('', 'src/alchemist/_version.py').__version__,
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
    # scripts=['bin/alchemist'],
    package_dir={'alchemist': 'src/alchemist'},
    packages=find_packages('src'),
    # entry_points={'pytest11': ['alchemist = alchemist.plugin']},
    dependency_links=[
        # wsgi_intercept
        # <https://code.google.com/p/wsgi-intercept/issues/detail?id=25>
        # 'git+git://github.com/concordusapps/wsgi-intercept.git'
        # '#egg=wsgi_intercept-0.6.0',

        'git+git://github.com/concordusapps/flask-script.git@edge'
        '#egg=flask-script-edge',
    ],
    install_requires=[
        # Cross-platform colored terminal text.
        # <https://pypi.python.org/pypi/colorama>
        # 'colorama',

        # ANSII Color formatting for output in terminal.
        # <https://pypi.python.org/pypi/termcolor>
        # 'termcolor >= 1.1, < 1.2',

        # Flask is a microframework for Python based on Werkzeug,
        # Jinja 2 and good intentions.
        # <http://flask.pocoo.org/>
        'flask >= 0.10',

        # Fast, simple object-to-object and broadcast signaling
        # <http://pythonhosted.org/blinker/>
        'blinker >= 1.3',

        # The Flask-Script extension provides support for writing external
        # scripts in Flask.
        # <http://flask-script.readthedocs.org/en/latest/>
        'flask-script == edge',

        # A simple flask extension to discover files in a declared
        # array of components.
        'flask-components >= 0.1',

        # The Python SQL Toolkit and Object Relational Mapper
        # <http://www.sqlalchemy.org/>
        'sqlalchemy >= 0.8',

        # SQLAlchemy utilities.
        # <https://github.com/kvesteri/sqlzalchemy-utils>.
        'sqlalchemy-utils >= 0.16',

        # Test runner.
        'pytest >= 2.4',

        # Ensure PEP8 conformance.
        'pytest-pep8 >= 1.0',

        # Ensure test coverage.
        'pytest-cov >= 1.6',

        # Installs a WSGI application that intercepts requests made to a
        # hostname and port combination for testing.
        # 'wsgi_intercept == 0.6.0',

        # A comprehensive HTTP client library that supports many features
        # left out of other HTTP libraries.
        # TODO: This is required by wsgi_intercept; either the requirement
        # needs to removed (preferred) or it needs to be folded into
        # wsgi_intercept.
        # 'httplib2',

        # Requests.
        # Requests takes all of the work out of Python HTTP/1.1 —
        # making your integration with web services seamless.
        # <http://docs.python-requests.org/en/latest/>
        # 'requests'
    ]
)
