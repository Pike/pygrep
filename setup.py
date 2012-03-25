#!/usr/bin/env python

from distutils.core import setup

setup(name='pygrep',
      version='0.1',
      description='Find python identifiers',
      author='Axel Hecht',
      author_email='axel@pike.org',
      url='http://github.com/Pike/pygrep',
      packages=['pygrep'],
      scripts=['scripts/pygrep'],
     )
