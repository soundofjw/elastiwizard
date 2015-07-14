from setuptools import setup, find_packages
from os import path

from elastiwizard import __version__ as ew_version


setup(
    name="Elastiwizard",
    version=ew_version,
    author="Adrian Moses",
    author_email="adrian@loudr.fm",
    description="Elasitiwizard converts natural language to elasticsearch aggregations",
    license="MIT License",
    url="https://github.com/ammoses89/elastiwizard",
    packages=find_packages(),
)
