import os
from setuptools import setup

setup(
    name="mds_provider_client",
    version=get_version(),
    description="Module implementing the MDS Provider API",
    author="City of Santa Monica and contributors",
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Environment :: Docker",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Natural Language :: English",
    ],
    verson="0.1.1"
)