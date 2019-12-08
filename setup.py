# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Thursday, 7th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import setuptools
from hostray import Version, __name__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=__name__,
    version=Version,
    author="hsky77",
    author_email="howardlkung@gmail.com",
    description="customized Tornado based web server utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hsky77/hostray",
    packages=setuptools.find_packages(),
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['tornado>=6.0.3',
                      'PyYAML>=5.1.1',
                      'sqlalchemy>=1.3.5',
                      'coloredlogs>=10.0',
                      'bson>=0.5.8',
                      'PyMySQL>=0.9.3'],
    python_requires='>=3.6',
    package_data={'': ['*.yaml', '*.csv']}
)
