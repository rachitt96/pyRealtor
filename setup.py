from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'pyRealtor',
    version = '0.1.0',
    description = 'Python package for fetching and analyzing REALTOR.CA MLS Listings',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = 'Rachit Trivedi',
    author_email = 'rachitt96@gmail.com',
    packages = ['pyRealtor'],
    python_requires = '>=3.6',
    install_requires = [
        'requests>=2.26.0',
        'pandas>=1.3.5',
        'numpy>=1.21.4'
    ],
    extras_required = {
        "dev": ["twine"]
    },
    include_package_data = True,
    package_data = {
        'pyRealtor': ['config/column_mapping_cfg.json']
    }
)