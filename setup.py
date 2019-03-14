import os
from setuptools import setup

setup(
    name="mds_provider_client",
    description="Module implementing the MDS Provider API",
    author="City of Santa Monica and contributors",
    install_requires=[
        "requests",
    ],
    packages=['mds_provider_client'],
    version="0.1.4"
)