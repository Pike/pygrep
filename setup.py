#!/usr/bin/env python

from setuptools import setup

CLASSIFIERS = """\
Intended Audience :: Developers
License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
"""

setup(name='pygrep',
      version='0.2',
      description='Find python identifiers',
      author='Axel Hecht',
      author_email='axel@pike.org',
      url='http://github.com/Pike/pygrep',
      packages=['pygrep'],
      scripts=['scripts/pygrep'],
      license="MPL 2.0",
      classifiers=CLASSIFIERS.splitlines(),
      platforms=["any"],
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
      install_requires=[
        'six'
      ],
     )
