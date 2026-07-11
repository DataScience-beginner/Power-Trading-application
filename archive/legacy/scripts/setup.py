#!/usr/bin/env python3
"""
Setup script for Power Trading Application
"""

from setuptools import setup, find_packages

setup(
    name="power-trading-parser",
    version="1.0.0",
    description="Universal parser for power trading Excel reports",
    author="DataScience-beginner",
    packages=find_packages(),
    install_requires=[
        'pandas>=2.0.0',
        'openpyxl>=3.1.0',
        'xlrd>=2.0.1',
        'jsonschema>=4.17.0',
        'python-dateutil>=2.8.2',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'parse-trading-data=run_parser:main',
        ],
    },
)
