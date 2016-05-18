#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "jsmin",
    "termcolor",
    "progressbar",
    "jsonmerge"
]

test_requirements = []

setup(
    name             = 'Heppi',
    version          = '0.4',
    description      = "High Energy Physics Plotting Interface",
    long_description = readme + '\n\n' + history,
    author           = "Yacine Haddad",
    author_email     = 'yhaddad@cern.ch',
    url              = 'https://github.com/yhaddad/Heppi',
    download_url     = 'https://github.com/yhaddad/Heppi/tarball/0.4',
    packages = [
        'heppi',
    ],
    package_dir          = {'heppi': 'heppi'},
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'plot = plot',
            #        'rootplotmpl = rootplot.core:cli_rootplotmpl',
            #        'tree2hists = rootplot.tree2hists:main',
            #        'rootinfo = rootplot.rootinfo:main'
        ]
    },
    install_requires    = requirements,
    license     = "ISCL",
    zip_safe    = False,
    keywords    = ['Heppi','heppi'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite    = 'tests',
    tests_require = test_requirements
)
