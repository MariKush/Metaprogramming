# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

import re
from setuptools import setup

version = re.search('^__version__\s*=\s*"(.*)"', open('CSharpCCF/main.py', encoding='utf-8').read(), re.M).group(1)

with open("README.rst", "r", encoding='utf-8') as f:
    long_descr = f.read()

setup(
    name="CSharpCCF",
    packages=["CSharpCCF"],
    entry_points={
        "console_scripts": ['CSharpCCF = CSharpCCF.main:main']
    },
    version=version,
    description="C# CCF",
    long_description=long_descr,
    author="Mariia Kushnirenko",
    author_email="kms1999@ukr.net",
    url="https://pypi.org/user/MariKush/",
)
