# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.cmd import Command
from distutils import sysconfig
import os
import sys
import subprocess
import glob

from fp import __version__

PACKAGE = "fp"
NAME = "fp"
DESCRIPTION = "fp 0.2.0"
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

files = glob.glob("fp/tests/Math/Accumulators/data/*.csv")
datafiles = [(os.path.join(packagePath, "fp/tests/Math/Accumulators/data"), files)]


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
            command = "coverage run fp/tests/testSuite.py& coverage report& coverage html"
        else:
            command = "coverage run fp/tests/testSuite.py; coverage report; coverage html"
        subprocess.Popen(command, shell=True)


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="commercial",
    url=URL,
    packages=['fp.API',
              'fp.AlgoTrading',
              'fp.DateUtilities',
              'fp.Enums',
              'fp.Env',
              'fp.Math',
              'fp.Math.Accumulators',
              'fp.Math.Distributions',
              'fp.Math.Timeseries',
              'fp.Patterns',
              'fp.PricingEngines',
              'fp.Analysis',
              'fp.Analysis.TechnicalAnalysis',
              'fp.Utilities',
              'fp.tests',
              'fp.tests.API',
              'fp.tests.DateUtilities',
              'fp.tests.Env',
              'fp.tests.Math',
              'fp.tests.Math.Accumulators',
              'fp.tests.Math.Distributions',
              'fp.tests.Math.Timeseries',
              'fp.tests.Analysis',
              'fp.tests.Analysis.TechnicalAnalysis',
              'fp.tests.PricingEngines'],
    py_modules=['fp.__init__', 'fp.tests.testSuite'],
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
