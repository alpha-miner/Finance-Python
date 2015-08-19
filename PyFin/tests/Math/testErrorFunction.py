# -*- coding: utf-8 -*-
u"""
Created on 2015-8-3

@author: cheng.li
"""

import unittest
from PyFin.Math.ErrorFunction import errorFunction


class TestErrorFunction(unittest.TestCase):
    def testErrorFunction(self):
        x = 1.7e-09
        self.assertAlmostEqual(errorFunction(x), 1.918245e-9, 15)

        x = 7
        self.assertAlmostEqual(errorFunction(x), 1.0, 12)

        x = -7
        self.assertAlmostEqual(errorFunction(x), -1.0, 12)
