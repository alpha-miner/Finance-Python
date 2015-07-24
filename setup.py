# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.cmd import Command
import sys

from finpy import __version__

PACKAGE = "finpy"
NAME = "finpy"
DESCRIPTION = "finpy 0.2.0"
AUTHOR = "cheng li"
AUTHOR_EMAIL = "cheng.li@datayes.com"
URL = "www.datayes.com"
VERSION = __version__


class test(Command):
    description = "test the distribution prior to install"

    user_options = [
        ('test-dir=', None,
         "directory that contains the test definitions"),
        ]

    def initialize_options(self):
        self.test_dir = 'tests'

    def finalize_options(self):
        sys.path.insert(0, self.test_dir)

    def run(self):
        module = __import__('testSuite', globals(), locals(), [''])
        module.test()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="commercial",
    url=URL,
    packages=['finpy.api',
              'finpy.AlgoTrading',
              'finpy.DateUtilities',
              'finpy.Enums',
              'finpy.Env',
              'finpy.Math',
              'finpy.Math.Distributions',
              'finpy.PricingEngines',
              'finpy.Risk'],
    py_modules=['finpy.__init__'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: PC test",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python 2.7/3.4",
        "Framework :: none",
    ],
    cmdclass={"test": test},
)