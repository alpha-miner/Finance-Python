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
NAME = "Finance-Python"
VERSION = __version__
DESCRIPTION = "PyFin " + VERSION
AUTHOR = "cheng li"
AUTHOR_EMAIL = "wegamekinglc@hotmail.com"
URL = 'https://github.com/ChinaQuants/Finance-Python'

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


def git_version():
    from subprocess import Popen, PIPE
    gitproc = Popen(['git', 'rev-parse','HEAD'], stdout=PIPE)
    (stdout, _) = gitproc.communicate()
    return stdout.strip()


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


class version_build(Command):

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
        git_ver = git_version()[:10]
        configFile = 'PyFin/__init__.py'

        file_handle = open(configFile, 'r')
        lines = file_handle.readlines()
        newFiles = []
        for line in lines:
            if line.startswith('__version__'):
                line = line.split('+')[0].rstrip()
                line = line + " + \"-" + git_ver + "\"\n"
            newFiles.append(line)
        file_handle.close()
        os.remove(configFile)
        file_handle = open(configFile, 'w')
        file_handle.writelines(newFiles)
        file_handle.close()



setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=['PyFin.API',
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
              'PyFin.Analysis.DataProviders',
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
              'PyFin.tests.Analysis.DataProviders',
              'PyFin.tests.Analysis.TechnicalAnalysis',
              'PyFin.tests.PricingEngines'],
    py_modules=['PyFin.__init__', 'PyFin.tests.testSuite'],
    data_files=datafiles,
    classifiers=[],
    cmdclass={"test": test,
              "version_build": version_build},
)
