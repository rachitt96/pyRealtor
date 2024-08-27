# Copyright (C) 2024 Rachit Trivedi <rachitt96@gmail.com>
# License: MIT, rachitt96@gmail.com

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'pyRealtor',
    version = '0.1.8',
    description = 'Python package for fetching and analyzing REALTOR.CA and REALTOR.COM MLS Listings',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = 'Rachit Trivedi',
    author_email = 'rachitt96@gmail.com',
    license = 'MIT',
    url = 'https://github.com/rachitt96/pyRealtor',
    packages = ['pyRealtor'],
    python_requires = '>=3.6',
    install_requires = [
        'requests>=2.26.0',
        'pandas>=1.3.5',
        'numpy>=1.21.4',
        'openpyxl>=3.1.2',
        'lxml>=5.1.0',
        'pyyaml>=6.0.1'
    ],
    extras_required = {
        "dev": ["twine"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    include_package_data = True,
    package_data = {
        'pyRealtor': [
            'config/column_mapping_cfg.json',
            'config/column_mapping_cfg_realtor_com.json',
            'config/graphql_queries.yml'
        ]
    }
)