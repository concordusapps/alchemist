#! /usr/bin/env python
import sys
from setuptools import setup, find_packages
from pkgutil import get_importer

# Ensure we have a minimum python version.
if sys.hexversion < 0x30302f0:  # 3.3.2
    raise RuntimeError(
        "'alchemist' requires at least version '3.3.2' of python")

# Load and append additional arguments for the setup function
# from the metadata module.
meta = get_importer('src/alchemist').find_module('meta').load_module()

setup(
    name='alchemist',
    version=meta.version,
    description=meta.description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3'
    ],
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/concordusapps/alchemist',
    scripts=['bin/alchemist'],
    package_dir={'alchemist': 'src/alchemist'},
    packages=find_packages('src'),
    entry_points={'pytest11': ['alchemist = alchemist.plugin']},
    dependency_links=(
        # wsgi_intercept
        # <https://code.google.com/p/wsgi-intercept/issues/detail?id=25>
        'git+git://github.com/concordusapps/wsgi-intercept.git'
        '#egg=wsgi_intercept-0.6.0',
    ),
    install_requires=(
        # Cross-platform colored terminal text.
        # <https://pypi.python.org/pypi/colorama>
        'colorama',

        # ANSII Color formatting for output in terminal.
        # <https://pypi.python.org/pypi/termcolor>
        'termcolor >= 1.1, < 1.2',

        # Flask is a microframework for Python based on Werkzeug,
        # Jinja 2 and good intentions.
        # <http://flask.pocoo.org/>
        'flask >= 0.10, < 0.11',

        # The Flask-Script extension provides support for writing external
        # scripts in Flask.
        # <http://flask-script.readthedocs.org/en/latest/>
        'flask-script >= 0.6.2',

        # The Python SQL Toolkit and Object Relational Mapper
        # <http://www.sqlalchemy.org/>
        'sqlalchemy >= 0.8, < 0.9',

        # SQLAlchemy utilities.
        # <https://github.com/kvesteri/sqlzalchemy-utils>.
        'sqlalchemy-utils',

        # Test runner.
        'pytest',

        # Ensure PEP8 conformance.
        'pytest-pep8',

        # Ensure test coverage.
        'pytest-cov',

        # Installs a WSGI application that intercepts requests made to a
        # hostname and port combination for testing.
        'wsgi_intercept == 0.6.0',

        # A comprehensive HTTP client library that supports many features
        # left out of other HTTP libraries.
        # TODO: This is required by wsgi_intercept; either the requirement
        # needs to removed (preferred) or it needs to be folded into
        # wsgi_intercept.
        'httplib2',

        # Requests.
        # Requests takes all of the work out of Python HTTP/1.1 —
        # making your integration with web services seamless.
        # <http://docs.python-requests.org/en/latest/>
        'requests'
    ),
)
