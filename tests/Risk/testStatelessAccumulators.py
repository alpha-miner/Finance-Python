# -*- coding: utf-8 -*-
u"""
Created on 2015-7-29

@author: cheng.li
"""

import unittest
import numpy as np
from finpy.Risk.StatelessAccumulators import Max
from finpy.Risk.StatelessAccumulators import Minimum
from finpy.Risk.StatelessAccumulators import Sum
from finpy.Risk.StatelessAccumulators import Variance
from finpy.Risk.StatelessAccumulators import Correlation


class TestStatelessAccumulators(unittest.TestCase):

    def testMax(self):
        samples = np.random.randn(1000)
        mm = Max(pNames='close')

        for i, value in enumerate(samples):
            mm.push(close=value)
            expected = max(samples[:i+1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected max:   {1:f}\n"
                                                             "calculated max: {2:f}".format(i, expected, calculated))

    def testMinimum(self):
        samples = np.random.randn(1000)
        mm = Minimum(pNames='close')

        for i, value in enumerate(samples):
            mm.push(close=value)
            expected = min(samples[:i+1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected min:   {1:f}\n"
                                                             "calculated min: {2:f}".format(i, expected, calculated))

    def testSum(self):
        samples = np.random.randn(1000)
        mm = Sum(pNames='close')

        for i, value in enumerate(samples):
            mm.push(close=value)
            expected = np.sum(samples[:i+1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected sum:   {1:f}\n"
                                                             "calculated sum: {2:f}".format(i, expected, calculated))

    def testVariance(self):
        samples = np.random.randn(1000)
        # np.var is population variance
        mm = Variance(pNames='close', isPopulation=True)

        for i, value in enumerate(samples):
            mm.push(close=value)
            expected = np.var(samples[:i+1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected var:   {1:f}\n"
                                                             "calculated var: {2:f}".format(i, expected, calculated))

    def testCorrelation(self):
        samplesOpen = np.random.randn(10000)
        samplesClose = np.random.randn(10000)
        mm = Correlation(pNames=['close', 'open'])

        for i, (openPrice, closePrice) in enumerate(zip(samplesOpen, samplesClose)):
            mm.push(open=openPrice, close=closePrice)
            if i >= 1:
                expected = np.corrcoef(samplesOpen[:i+1], samplesClose[:i+1])[0,1]
                calculated = mm.result()
                self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                                 "expected correlation:   {1:f}\n"
                                                                 "calculated correlation: {2:f}".format(i, expected, calculated))
