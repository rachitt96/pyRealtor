from setuptools import setup

setup(
    name = 'pyRealtor',
    version = '0.1.0',
    description = 'Python package for automatically fetching and analyzing MLS Listings',
    author = 'Rachit Trivedi',
    author_email = 'rachitt96@gmail.com',
    packages = ['pyRealtor'],
    install_requires = [
        'requests',
        'pandas',
        'numpy'
    ],
    extras_required = {
        "dev": ["twine"]
    },
    include_package_data = True,
    package_data = {
        'pyRealtor': ['config/column_mapping_cfg.json']
    }
)