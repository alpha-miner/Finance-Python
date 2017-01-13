# -*- coding: utf-8 -*-
u"""
Created on 2017-1-13

@author: cheng.li
"""

import unittest
import warnings
from PyFin.Utilities import pyFinAssert
from PyFin.Utilities import pyFinWarning
from PyFin.Utilities import isClose


class TestAsserts(unittest.TestCase):

    def testPyFinAssert(self):

        with self.assertRaises(ValueError):
            pyFinAssert(1 == 2, ValueError)

    def testPyFinWarning(self):
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            pyFinWarning(1 == 2, DeprecationWarning)
            self.assertTrue(any(item.category == DeprecationWarning for item in warning_list))

    def testIsClose(self):
        self.assertTrue(isClose(1.0, 1.000001, 1e-5))
        self.assertTrue(isClose(1e9, 1. + 1e9, 1e-5, 1e-6))
        self.assertFalse(isClose(1., 1. + 1e-5, 1e-6, 1e-6))