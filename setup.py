#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='slipstream',
    version='0.1.0',
    description='A Python static page generator designed to publish blags from http://draftin.com',
    long_description=readme + '\n\n' + history,
    author='Wayne Werner',
    author_email='waynejwerner@gmail.com',
    url='https://github.com/waynew/slipstream',
    packages=[
        'slipstream',
    ],
    entry_points={
        'console_scripts': [
            'slipstream = slipstream.slipstream:run',
        ],
    },
    cmdclass={'test': PyTest},
    package_dir={'slipstream': 'slipstream'},
    include_package_data=True,
    install_requires=['flask', 'flask-login'
    ],
    license="GPLv3",
    zip_safe=False,
    keywords='draft flask blog publish static-site',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=['pytest', 'hypothesis', 'pytest-cov'],
)
