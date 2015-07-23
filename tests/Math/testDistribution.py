# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

import unittest
import math
from finpy.Math.MathConstants import _M_PI

average = 1.0
sigma = 2.0

def gaussia(x):

    normFact = sigma*math.sqrt(2.0 * _M_PI)
    dx = x - average
    return math.exp(-dx*dx/(2.0*sigma*sigma))/normFact

def gaussianDerivative(x):
    normFact = sigma*sigma*sigma*math.sqrt(2.0*_M_PI)
    dx = x-average;
    return -dx*math.exp(-dx*dx/(2.0*sigma*sigma))/normFact;


class TestDistribution(unittest.TestCase):

    def testNormal(self):
        pass