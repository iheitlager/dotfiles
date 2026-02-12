"""Setup script for arch package."""

from setuptools import setup, find_packages

setup(
    name="arch",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "jsonschema>=4.0.0",
    ],
)
