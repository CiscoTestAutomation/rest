#! /usr/bin/env python

"""Setup file for rest package

See:
    https://packaging.python.org/en/latest/distributing.html
"""

import os
import re
import sys
import shlex
import unittest
import subprocess
from setuptools import setup, find_packages, Command
from setuptools.command.test import test

pkg_name = 'rest.connector'
pkg_path = '/'.join(pkg_name.split('.'))


class CleanCommand(Command):
    '''Custom clean command

    cleanup current directory:
        - removes build/
        - removes src/*.egg-info
        - removes *.pyc and __pycache__ recursively

    Example
    -------
        python setup.py clean

    '''

    user_options = []
    description = 'CISCO SHARED : Clean all build artifacts'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./src/*.egg-info')
        os.system('find . -type f -name "*.pyc" | xargs rm -vrf')
        os.system('find . -type d -name "__pycache__" | xargs rm -vrf')


class TestCommand(Command):
    user_options = []
    description = 'CISCO SHARED : Run unit tests against this package'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # where the tests are (relative to here)
        tests = os.path.join('src', pkg_path, 'tests')

        # call unittests
        sys.exit(unittest.main(
            module=None,
            argv=['python -m unittest', 'discover', tests],
            failfast=True))


def read(*paths):
    '''read and return txt content of file'''
    with open(os.path.join(os.path.dirname(__file__), *paths)) as fp:
        return fp.read()


def find_version(*paths):
    '''reads a file and returns the defined __version__ value'''
    version_match = re.search(r"^__version__ ?= ?['\"]([^'\"]*)['\"]",
                              read(*paths), re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# launch setup
setup(
    name=pkg_name,
    version=find_version('src', pkg_path, '__init__.py'),

    # descriptions
    description='pyATS REST connection package',
    long_description=read('DESCRIPTION.rst'),

    # the package's documentation page.
    url='https://developer.cisco.com/docs/rest-connector/',

    # author details
    author='Cisco Systems Inc.',
    author_email='jeaubin@cisco.com',
    maintainer_email='pyats-support-ext@cisco.com',

    # project licensing
    license='Apache 2.0',

    platforms=['Linux', 'macOS'],

    # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 6 - Mature',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # uses namespace package
    namespace_packages=['rest'],

    # project keywords
    keywords='pyats cisco-shared',

    # project packages
    packages=find_packages(where='src'),

    # project directory
    package_dir={
        '': 'src',
    },

    # additional package data files that goes into the package itself
    package_data={'': ['README.md',
                       'tests/testbed.yaml',
                       ]
                  },

    # Standalone scripts
    scripts=[
    ],

    # console entry point
    entry_points={
    },

    # package dependencies
    install_requires=[
        'requests >= 1.15.1',
        'dict2xml',
        'f5-icontrol-rest',
    ],

    # any additional groups of dependencies.
    # install using: $ pip install -e .[dev]
    extras_require={
        'dev': ['coverage',
                'restview',
                'Sphinx',
                'sphinx-rtd-theme',
                'requests-mock'],
    },

    # any data files placed outside this package.
    # See: http://docs.python.org/3.4/distutils/setupscript.html
    # format:
    #   [('target', ['list', 'of', 'files'])]
    # where target is sys.prefix/<target>
    data_files=[],

    # custom commands for setup.py
    cmdclass={
        'clean': CleanCommand,
        'test': TestCommand,
    },

    # non zip-safe (never tested it)
    zip_safe=False,
)
