# -*- coding: utf-8 -*-
u"""
Created on 2015-7-29

@author: cheng.li
"""

import unittest
import numpy as np
from PyFin.Math.Accumulators.StatelessAccumulators import Max
from PyFin.Math.Accumulators.StatelessAccumulators import Minimum
from PyFin.Math.Accumulators.StatelessAccumulators import Sum
from PyFin.Math.Accumulators.StatelessAccumulators import Variance
from PyFin.Math.Accumulators.StatelessAccumulators import Correlation


class TestStatelessAccumulators(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.samplesOpen = np.random.randn(1000)
        self.samplesClose = np.random.randn(1000)

    def testMax(self):
        mm = Max(dependency='close')

        for i, value in enumerate(self.samplesClose):
            mm.push(dict(close=value))
            expected = max(self.samplesClose[:i + 1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected max:   {1:f}\n"
                                                             "calculated max: {2:f}".format(i, expected, calculated))

    def testMinimum(self):
        mm = Minimum(dependency='close')

        for i, value in enumerate(self.samplesClose):
            mm.push(dict(close=value))
            expected = min(self.samplesClose[:i + 1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected min:   {1:f}\n"
                                                             "calculated min: {2:f}".format(i, expected, calculated))

    def testSum(self):
        mm = Sum(dependency='close')

        for i, value in enumerate(self.samplesClose):
            mm.push(dict(close=value))
            expected = np.sum(self.samplesClose[:i + 1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected sum:   {1:f}\n"
                                                             "calculated sum: {2:f}".format(i, expected, calculated))

    def testVariance(self):
        # np.var is population variance
        mm = Variance(dependency='close', isPopulation=True)
        mm2 = Variance(dependency='close', )

        for i, value in enumerate(self.samplesClose):
            mm.push(dict(close=value))
            mm2.push(dict(close=value))
            expected = np.var(self.samplesClose[:i + 1])
            calculated = mm.result()

            if i == 0:
                with self.assertRaises(ArithmeticError):
                    _ = mm2.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected var:   {1:f}\n"
                                                             "calculated var: {2:f}".format(i, expected, calculated))

            if i >= 1:
                calculated = mm2.result() * i / (i + 1)  # transform sample variance to population variance
                self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                                 "expected var:   {1:f}\n"
                                                                 "calculated var: {2:f}".format(i, expected,
                                                                                                calculated))

    def testCorrelation(self):
        mm = Correlation(dependency=['close', 'open'])

        for i, (openPrice, closePrice) in enumerate(zip(self.samplesOpen, self.samplesClose)):
            mm.push(dict(open=openPrice, close=closePrice))
            if i == 0:
                with self.assertRaises(ArithmeticError):
                    _ = mm.result()
            if i >= 1:
                expected = np.corrcoef(self.samplesOpen[:i + 1], self.samplesClose[:i + 1])[0, 1]
                calculated = mm.result()
                self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                                 "expected correlation:   {1:f}\n"
                                                                 "calculated correlation: {2:f}".format(i, expected,
                                                                                                        calculated))
