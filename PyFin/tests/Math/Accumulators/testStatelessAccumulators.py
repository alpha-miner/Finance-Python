# -*- coding: utf-8 -*-
u"""
Created on 2015-7-29

@author: cheng.li
"""

import unittest
import math
import numpy as np
from PyFin.Math.Accumulators.StatelessAccumulators import Average
from PyFin.Math.Accumulators.StatelessAccumulators import XAverage
from PyFin.Math.Accumulators.StatelessAccumulators import Max
from PyFin.Math.Accumulators.StatelessAccumulators import Minimum
from PyFin.Math.Accumulators.StatelessAccumulators import Diff
from PyFin.Math.Accumulators.StatelessAccumulators import SimpleReturn
from PyFin.Math.Accumulators.StatelessAccumulators import LogReturn
from PyFin.Math.Accumulators.StatelessAccumulators import Sum
from PyFin.Math.Accumulators.StatelessAccumulators import Variance
from PyFin.Math.Accumulators.StatelessAccumulators import Correlation
from PyFin.Math.Accumulators.StatelessAccumulators import Product
from PyFin.Math.Accumulators.StatelessAccumulators import CenterMoment
from PyFin.Math.Accumulators.StatelessAccumulators import Skewness
from PyFin.Math.Accumulators.StatelessAccumulators import Kurtosis
from PyFin.Math.Accumulators.StatelessAccumulators import Rank
from PyFin.Math.Accumulators.StatelessAccumulators import LevelList
from PyFin.Math.Accumulators.StatelessAccumulators import LevelValue
from PyFin.Math.Accumulators.StatelessAccumulators import AutoCorrelation


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

    def testDiff(self):
        mm = Diff(dependency='close')
        current = np.nan
        for i, value in enumerate(self.samplesClose):
            mm.push(dict(close=value))
            previous = current
            current = value

            if not np.isnan(previous):
                expected = current - previous
                calculated = mm.result()

                self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                                 "expected min:   {1:f}\n"
                                                                 "calculated diff: {2:f}".format(i, expected,
                                                                                                 calculated))

    def testSimpleReturn(self):
        mm = SimpleReturn(dependency='close')
        current = np.nan
        for i, value in enumerate(self.samplesClose):
            mm.push(dict(close=value))
            previous = current
            current = value

            if not np.isnan(previous):
                expected = current / previous - 1.
                calculated = mm.result()

                self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                                 "expected min:   {1:f}\n"
                                                                 "calculated simple return: {2:f}".format(i, expected,
                                                                                                          calculated))

    def testLogReturn(self):
        mm = LogReturn(dependency='close')
        current = np.nan
        for i, value in enumerate(self.samplesClose):
            previous = current
            current = abs(value)
            mm.push(dict(close=current))

            if not np.isnan(previous):
                expected = math.log(current / previous)
                calculated = mm.result()

                self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                                 "expected min:   {1:f}\n"
                                                                 "calculated log return: {2:f}".format(i, expected,
                                                                                                       calculated))

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

    def testProduct(self):
        product = Product(dependency='close')
        expected = 1
        for i, value in enumerate(self.samplesClose):
            product.push(dict(close=value))
            calculated = product.result()
            expected *= value
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected product:   {1:f}\n"
                                                             "calculated product: {2:f}".format(i, expected,
                                                                                                calculated))

    def testCenterMoment(self):
        order = 1
        moment = CenterMoment(order, dependency='close')
        tmp_list = []
        for i, value in enumerate(self.samplesClose):
            moment.push(dict(close=value))
            calculated = moment.result()
            tmp_list.append(value)
            expected = np.mean(np.power(np.abs(np.array(tmp_list) - np.mean(tmp_list)), order))
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected moment:   {1:f}\n"
                                                             "calculated moment: {2:f}".format(i, expected,
                                                                                                  calculated))
        order = 2
        moment = CenterMoment(order, dependency='close')
        tmp_list = []
        for i, value in enumerate(self.samplesClose):
            moment.push(dict(close=value))
            calculated = moment.result()
            tmp_list.append(value)
            expected = np.mean(np.power(np.abs(np.array(tmp_list) - np.mean(tmp_list)), order))
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected moment:   {1:f}\n"
                                                             "calculated moment: {2:f}".format(i, expected,
                                                                                                calculated))
        order = 3
        moment = CenterMoment(order, dependency='close')
        tmp_list = []
        for i, value in enumerate(self.samplesClose):
            moment.push(dict(close=value))
            calculated = moment.result()
            tmp_list.append(value)
            expected = np.mean(np.power(np.abs(np.array(tmp_list) - np.mean(tmp_list)), order))
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected moment:   {1:f}\n"
                                                             "calculated moment: {2:f}".format(i, expected,
                                                                                                calculated))


    def testSkewness(self):
        skewness = Skewness(dependency='close')
        close_list = []

        for i, value in enumerate(self.samplesClose):
            close_list.append(value)
            skewness.push(dict(close=value))
            calculated = skewness.result()
            this_moment3 = np.mean(np.power(np.abs(np.array(close_list) - np.mean(close_list)), 3))
            if i == 0:
                self.assertTrue(np.isnan(calculated))
            if i >= 1:
                expected = this_moment3 / np.power(np.std(close_list), 3)
                self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                                    "expected skewness:   {1:f}\n"
                                                                    "calculated skewness: {2:f}".format(i, expected,
                                                                                                        calculated))


    def testKurtosis(self):
        kurtosis = Kurtosis(dependency='close')
        close_list = []

        for i, value in enumerate(self.samplesClose):
            close_list.append(value)
            kurtosis.push(dict(close=value))
            calculated = kurtosis.result()
            this_moment4 = np.mean(np.power(np.abs(np.array(close_list) - np.mean(close_list)), 4))
            if i == 0:
                self.assertTrue(np.isnan(calculated))
            if i >= 1:
                expected = this_moment4 / np.power(np.std(close_list), 4)
                self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                                    "expected skewness:   {1:f}\n"
                                                                    "calculated skewness: {2:f}".format(i, expected,
                                                                                                        calculated))

    def testRank(self):
        rank = Rank(dependency='close')
        close_list = []

        for i, value in enumerate(self.samplesClose):
            close_list.append(value)
            rank.push(dict(close=value))
            calculated = rank.result()
            expected = np.argsort(np.argsort(close_list))
            self.assertListEqual(list(expected), calculated, "at index {0:d}\n"
                                                             "expected rank:   {1}\n"
                                                             "calculated rank: {2}".format(i, expected,
                                                                                             calculated))


    def testLevelList(self):
        levelList = LevelList(dependency='close')
        first_value = self.samplesClose[0]
        expected = []
        calculated = []

        for i, value in enumerate(self.samplesClose):
            levelList.push(dict(close=value))
            if i == 0:
                expected.append(1.0)
            else:
                expected.append(value / first_value)
            calculated = levelList.result()
            self.assertListEqual(expected, calculated, "at index {0}\n"
                                                        "expected levelList:  {1}\n"
                                                        "calculated levelList:{2}".format(i, expected, calculated))


    def testLevelValue(self):
        levelValue = LevelValue(dependency='close')
        first_value = self.samplesClose[0]

        for i, value in enumerate(self.samplesClose):
            levelValue.push(dict(close=value))
            if i == 0:
                expected = 1.0
            else:
                expected = value / first_value
            calculated = levelValue.result()
            self.assertAlmostEqual(expected, calculated, 10, "at index of {0:d}\n"
                                                            "expected levelValue:  {1:f}\n"
                                                            "calculated levelValue:{2:f}".format(i, expected, calculated))


    def testAutoCorrelation(self):
        lags = 2
        autoCorr = AutoCorrelation(lags, dependency='close')
        con = []

        for i, value in enumerate(self.samplesClose):
            con.append(value)
            autoCorr.push(dict(close=value))
            if i >= lags + 2:
                con_forward = con[0:len(con) - lags]
                con_backward = con[-len(con) + lags - 1:-1]
                expected = np.cov(con_forward, con_backward) / (np.std(con_forward) * np.std(con_backward))
                calculated = autoCorr.result()
                self.assertAlmostEqual(expected[0, 1], calculated, 10, "at index of {0:d}\n"
                                                                "expected autoCorr:   {1:f}\n"
                                                                "calculated autoCorr: {2:f}".format(i, expected[0, 1],
                                                                                                    calculated))

if __name__ == '__main__':
    unittest.main()
