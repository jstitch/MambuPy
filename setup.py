#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:license: GPLv3, see LICENSE for more details.
"""

import os
import sys

import setuptools

from MambuPy import __version__


def readme():
    """print long description"""
    try:
        import m2r2
    except ImportError:
        with open("README.md") as f:
            return f.read()

    with open("README.md") as f:
        return m2r2.convert(f.read())


class VerifyVersionCommand:
    """Custom command to verify that the git tag matches our version"""

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("CIRCLE_TAG")
        if tag != __version__:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, __version__
            )
            sys.exit(info)

packages=[
    "MambuPy",
    "MambuPy/rest",
    "MambuPy/orm",
    "mambupy",
    "mambupy/rest",
    "mambupy/orm",
    ]
if int(__version__[0]) >= 2:
    packages.extend(
        ["MambuPy/api",
         "mambupy/api",
         "MambuPy/api/connector",
         "mambupy/api/connector",
         "MambuPy/rest1to2",
         "mambupy/rest1to2",
         ])

install_requires=[
    "future",
    "requests==2.26.0",
    "requests_toolbelt==0.9.1",
    "SQLAlchemy>=1.3.6",
    ]
if int(__version__[0]) <= 3:
    install_requires.extend(
        ["mysqlclient",
         ])
else:
    install_requires.extend(
        ["mysqlclient==2.1.0",
         ])

setuptools.setup(
    name="MambuPy",
    version=__version__,
    description="A python lib for using Mambu APIs.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://mambupydocs.readthedocs.io",
    author="Javier Novoa C.",
    author_email="jstitch@gmail.com",
    license="GPLv3",
    keywords=[
        "mambu",
    ],
    packages=packages,
    python_requires=">=2.7",
    cmdclass={"verify": VerifyVersionCommand},
    install_requires=install_requires,
)
