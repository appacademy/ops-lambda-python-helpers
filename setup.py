#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    'jsonschema>=2.6.0,<2.7.0',
    'pandas>=0.23.0,<0.24.0'
]

packages = ['ops_helpers']

setup(
    name="ops-lambda-python-helpers",
    version="0.0.11",
    author="David Fort",
    author_email="ptiger10@gmail.com",
    description="Helper functions for use with ops lambda functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=packages,
    incude_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requires,
)
