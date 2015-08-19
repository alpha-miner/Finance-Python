# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.cmd import Command
from distutils import sysconfig
import os
import sys
import subprocess
import glob

from PyFin import __version__

PACKAGE = "PyFin"
NAME = "PyFin"
DESCRIPTION = "PyFin " + __version__
AUTHOR = "cheng li"
AUTHOR_EMAIL = "cheng.li@datayes.com"
URL = 'https://code.csdn.net/wegamekinglc/finance-python'
DOWNLOAD_URL = 'https://code.csdn.net/wegamekinglc/finance-python/tree/0.3.1'
VERSION = __version__

if os.name == "posix":
    exePath = sys.path
    for path in exePath:
        if path.endswith('site-packages'):
            packagePath = path
            break
else:
    packagePath = sysconfig.get_python_lib()

files = glob.glob("PyFin/tests/Math/Accumulators/data/*.csv")
datafiles = [(os.path.join(packagePath, "PyFin/tests/Math/Accumulators/data"), files)]


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
            command = "coverage run PyFin/tests/testSuite.py& coverage report& coverage html"
        else:
            command = "coverage run PyFin/tests/testSuite.py; coverage report; coverage html"
        subprocess.Popen(command, shell=True)


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="commercial",
    url=URL,
    download_url=DOWNLOAD_URL,
    packages=['PyFin.API',
              'PyFin.AlgoTrading',
              'PyFin.DateUtilities',
              'PyFin.Enums',
              'PyFin.Env',
              'PyFin.Math',
              'PyFin.Math.Accumulators',
              'PyFin.Math.Distributions',
              'PyFin.Math.Timeseries',
              'PyFin.Patterns',
              'PyFin.PricingEngines',
              'PyFin.Analysis',
              'PyFin.Analysis.TechnicalAnalysis',
              'PyFin.Utilities',
              'PyFin.tests',
              'PyFin.tests.API',
              'PyFin.tests.DateUtilities',
              'PyFin.tests.Env',
              'PyFin.tests.Math',
              'PyFin.tests.Math.Accumulators',
              'PyFin.tests.Math.Distributions',
              'PyFin.tests.Math.Timeseries',
              'PyFin.tests.Analysis',
              'PyFin.tests.Analysis.TechnicalAnalysis',
              'PyFin.tests.PricingEngines'],
    py_modules=['PyFin.__init__', 'PyFin.tests.testSuite'],
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
