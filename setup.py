# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.cmd import Command
from distutils import sysconfig
import os
import sys
import subprocess
import glob

from finpy import __version__

PACKAGE = "finpy"
NAME = "finpy"
DESCRIPTION = "finpy 0.2.0"
AUTHOR = "cheng li"
AUTHOR_EMAIL = "cheng.li@datayes.com"
URL = "www.datayes.com"
VERSION = __version__

if os.name == "posix":
    exePath = sys.path
    for path in exePath:
        if path.endswith('site-packages'):
            packagePath = path
            break
else:
    packagePath = sysconfig.get_python_lib()

files = glob.glob("finpy/tests/Math/Accumulators/data/*.csv")
datafiles = [(os.path.join(packagePath, "finpy/tests/Math/Accumulators/data"), files)]


class test(Command):
    description = "test the distribution prior to install"

    user_options = [
        ('test-dir=', None,
         "directory that contains the test definitions"),
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if sys.platform == 'win32':
            command = "coverage run finpy/tests/testSuite.py& coverage report& coverage html"
        else:
            command = "coverage run finpy/tests/testSuite.py; coverage report; coverage html"
        subprocess.Popen(command, shell=True)


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="commercial",
    url=URL,
    packages=['finpy.API',
              'finpy.AlgoTrading',
              'finpy.DateUtilities',
              'finpy.Enums',
              'finpy.Env',
              'finpy.Math',
              'finpy.Math.Accumulators',
              'finpy.Math.Distributions',
              'finpy.Math.Timeseries',
              'finpy.Patterns',
              'finpy.PricingEngines',
              'finpy.Analysis',
              'finpy.Analysis.TechnicalAnalysis',
              'finpy.Utilities',
              'finpy.tests',
              'finpy.tests.API',
              'finpy.tests.DateUtilities',
              'finpy.tests.Env',
              'finpy.tests.Math',
              'finpy.tests.Math.Accumulators',
              'finpy.tests.Math.Distributions',
              'finpy.tests.Math.Timeseries',
              'finpy.tests.Analysis',
              'finpy.tests.Analysis.TechnicalAnalysis',
              'finpy.tests.PricingEngines'],
    py_modules=['finpy.__init__', 'finpy.tests.testSuite'],
    data_files=datafiles,
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
