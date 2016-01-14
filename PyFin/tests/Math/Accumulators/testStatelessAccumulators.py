# -*- coding: utf-8 -*-
u"""
Created on 2015-7-29

@author: cheng.li
"""

import unittest
import numpy as np
from PyFin.Math.Accumulators.StatelessAccumulators import Average
from PyFin.Math.Accumulators.StatelessAccumulators import XAverage
from PyFin.Math.Accumulators.StatelessAccumulators import MACD
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

    def testAverage(self):
        average = Average(dependency='close')

        for i, value in enumerate(self.samplesClose):
            average.push(dict(close=value))
            expected = np.mean(self.samplesClose[:i + 1])

            calculated = average.result()
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected average:   {1:f}\n"
                                                             "calculated average: {2:f}".format(i,
                                                                                                  expected,
                                                                                                  calculated))

    def testXAverage(self):
        xaverage = XAverage(window=5, dependency='close')
        exp_weight = 2.0 / 6.0

        for i, value in enumerate(self.samplesClose):
            xaverage.push(dict(close=value))
            if i == 0:
                expected = self.samplesClose[i]
            else:
                expected += exp_weight * (self.samplesClose[i] - expected)

            calculated = xaverage.result()
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected x-average:   {1:f}\n"
                                                             "calculated x-average: {2:f}".format(i,
                                                                                                  expected,
                                                                                                  calculated))

    def testMACD(self):
        macd = MACD(short=5, long=10, dependency='close')
        short_average = XAverage(window=5, dependency='close')
        long_average = XAverage(window=10, dependency='close')

        for i, value in enumerate(self.samplesClose):
            macd.push(dict(close=value))
            short_average.push(dict(close=value))
            long_average.push(dict(close=value))
            expected = short_average.result() - long_average.result()

            calculated = macd.result()
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected x-average:   {1:f}\n"
                                                             "calculated x-average: {2:f}".format(i,
                                                                                                  expected,
                                                                                                  calculated))

    def testEMAMACD(self):
        fast = 5
        slow = 10
        ema_window = 10
        macd = MACD(fast, slow, 'close')
        ema_macd = XAverage(ema_window, macd)

        macd_diff = macd - ema_macd

        for i, value in enumerate(self.samplesClose):
            macd.push(dict(close=value))
            ema_macd.push(dict(close=value))
            macd_diff.push(dict(close=value))
            expected = macd.value - ema_macd.value
            calculated = macd_diff.value
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected ema macd diff:   {1:f}\n"
                                                             "calculated ema macd diff: {2:f}".format(i, expected, calculated))

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
                self.assertTrue(np.isnan(mm2.result()))

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
                self.assertTrue(np.isnan(mm.result()))
            if i >= 1:
                expected = np.corrcoef(self.samplesOpen[:i + 1], self.samplesClose[:i + 1])[0, 1]
                calculated = mm.result()
                self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                                 "expected correlation:   {1:f}\n"
                                                                 "calculated correlation: {2:f}".format(i, expected,
                                                                                                        calculated))
