# -*- coding: utf-8 -*-

from setuptools import setup
from distutils.cmd import Command
from distutils import sysconfig
import os
import sys
import io
import subprocess
import glob
import numpy as np
from Cython.Build import cythonize

PACKAGE = "PyFin"
NAME = "Finance-Python"
VERSION = "0.4.3"
DESCRIPTION = "PyFin " + VERSION
AUTHOR = "cheng li"
AUTHOR_EMAIL = "wegamekinglc@hotmail.com"
URL = 'https://github.com/ChinaQuants/Finance-Python'

packagePath = sysconfig.get_python_lib()

files = glob.glob("PyFin/tests/Math/Accumulators/data/*.csv")
datafiles = [
    (os.path.join(packagePath, "PyFin/tests/Math/Accumulators/data"), files)]

files = glob.glob("PyFin/tests/POpt/data/*.csv")
datafiles.append((os.path.join(packagePath, "PyFin/tests/POpt/data"), files))


def git_version():
    from subprocess import Popen, PIPE
    gitproc = Popen(['git', 'rev-parse', 'HEAD'], stdout=PIPE)
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
        process = subprocess.Popen(command, shell=True)
        process.wait()


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

if sys.version_info > (3, 0, 0):
    requirements = "requirements/py3.txt"
else:
    requirements = "requirements/py2.txt"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=['PyFin.api',
              'PyFin.examples',
              'PyFin.DateUtilities',
              'PyFin.Enums',
              'PyFin.Env',
              'PyFin.Math',
              'PyFin.Math.Accumulators',
              'PyFin.Math.Distributions',
              'PyFin.Math.Timeseries',
              'PyFin.Patterns',
              'PyFin.POpt',
              'PyFin.PricingEngines',
              'PyFin.Analysis',
              'PyFin.Analysis.DataProviders',
              'PyFin.Analysis.TechnicalAnalysis',
              'PyFin.Utilities',
              'PyFin.tests',
              'PyFin.tests.api',
              'PyFin.tests.DateUtilities',
              'PyFin.tests.Env',
              'PyFin.tests.Math',
              'PyFin.tests.Math.Accumulators',
              'PyFin.tests.Math.Distributions',
              'PyFin.tests.Math.Timeseries',
              'PyFin.tests.POpt',
              'PyFin.tests.Analysis',
              'PyFin.tests.Analysis.DataProviders',
              'PyFin.tests.Analysis.TechnicalAnalysis',
              'PyFin.tests.PricingEngines'],
    py_modules=['PyFin.__init__', 'PyFin.tests.testSuite'],
    install_requires=io.open(requirements, encoding='utf8').read(),
    data_files=datafiles,
    classifiers=[],
    cmdclass={"test": test,
              "version_build": version_build},
    ext_modules=cythonize(["PyFin/Math/Accumulators/impl.pyx",
                           "PyFin/DateUtilities/Date.pyx",
                           "PyFin/Utilities/Asserts.pyx",
                           "PyFin/Math/ErrorFunction.pyx"]),
    include_dirs=[np.get_include()]
)
