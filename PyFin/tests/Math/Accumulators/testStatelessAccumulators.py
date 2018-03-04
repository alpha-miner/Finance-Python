# -*- coding: utf-8 -*-
u"""
Created on 2015-7-29

@author: cheng.li
"""

import unittest
import copy
import pickle
import tempfile
import os
import math
import numpy as np
from PyFin.Math.Accumulators.IAccumulators import Sign
from PyFin.Math.Accumulators.IAccumulators import Latest
from PyFin.Math.Accumulators.StatelessAccumulators import Average
from PyFin.Math.Accumulators.StatelessAccumulators import XAverage
from PyFin.Math.Accumulators.StatelessAccumulators import Max
from PyFin.Math.Accumulators.StatelessAccumulators import Maximum
from PyFin.Math.Accumulators.StatelessAccumulators import Min
from PyFin.Math.Accumulators.StatelessAccumulators import Minimum
from PyFin.Math.Accumulators.StatelessAccumulators import Diff
from PyFin.Math.Accumulators.StatelessAccumulators import SimpleReturn
from PyFin.Math.Accumulators.StatelessAccumulators import LogReturn
from PyFin.Math.Accumulators.StatelessAccumulators import Sum
from PyFin.Math.Accumulators.StatelessAccumulators import Variance
from PyFin.Math.Accumulators.StatelessAccumulators import Product


class TestStatelessAccumulators(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.samplesOpen = np.random.randn(1000)
        self.samplesClose = np.random.randn(1000)

    def testAverage(self):
        average = Average('close')

        for i, value in enumerate(self.samplesClose):
            average.push(dict(close=value))
            expected = np.mean(self.samplesClose[:i + 1])

            calculated = average.result()
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected average:   {1:f}\n"
                                                             "calculated average: {2:f}".format(i,
                                                                                                expected,
                                                                                                calculated))

    def testSign(self):
        sign = Sign('close')

        for i, value in enumerate(self.samplesClose):
            sign.push(dict(close=value))
            expected = np.sign(self.samplesClose[i])

            calculated = sign.result()
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected average:   {1:f}\n"
                                                             "calculated average: {2:f}".format(i,
                                                                                                expected,
                                                                                                calculated))

    def testXAverage(self):
        xaverage = XAverage(5, 'close')
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
        mm = Max('close')

        for i, value in enumerate(self.samplesClose):
            mm.push(dict(close=value))
            expected = max(self.samplesClose[:i + 1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected max:   {1:f}\n"
                                                             "calculated max: {2:f}".format(i, expected, calculated))

    def testMaximum(self):
        mm = Maximum(x='open', y='close')

        for i, value in enumerate(zip(self.samplesOpen, self.samplesClose)):
            mm.push(dict(open=value[0], close=value[1]))
            expected = max(self.samplesOpen[i], self.samplesClose[i])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected max:   {1:f}\n"
                                                             "calculated max: {2:f}".format(i, expected, calculated))

    def testMaximumWithAccumulator(self):
        mm = Maximum(x=Latest('open'), y=Latest('close'))

        for i, value in enumerate(zip(self.samplesOpen, self.samplesClose)):
            mm.push(dict(open=value[0], close=value[1]))
            expected = max(self.samplesOpen[i], self.samplesClose[i])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected max:   {1:f}\n"
                                                             "calculated max: {2:f}".format(i, expected, calculated))

    def testMin(self):
        mm = Min('close')

        for i, value in enumerate(self.samplesClose):
            mm.push(dict(close=value))
            expected = min(self.samplesClose[:i + 1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected min:   {1:f}\n"
                                                             "calculated min: {2:f}".format(i, expected, calculated))

    def testMinimum(self):
        mm = Minimum(x='open', y='close')

        for i, value in enumerate(zip(self.samplesOpen, self.samplesClose)):
            mm.push(dict(open=value[0], close=value[1]))
            expected = min(self.samplesOpen[i], self.samplesClose[i])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected max:   {1:f}\n"
                                                             "calculated max: {2:f}".format(i, expected, calculated))

    def testMinimumWithAccumulator(self):
        mm = Minimum(x=Latest('open'), y=Latest('close'))

        for i, value in enumerate(zip(self.samplesOpen, self.samplesClose)):
            mm.push(dict(open=value[0], close=value[1]))
            expected = min(self.samplesOpen[i], self.samplesClose[i])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected max:   {1:f}\n"
                                                             "calculated max: {2:f}".format(i, expected, calculated))

    def testDiff(self):
        mm = Diff('close')
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

    def testDiffDeepcopy(self):
        mv = Diff('x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

        for i in np.random.rand(30):
            mv.push(dict(x=float(i)))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

    def testDiffPickle(self):
        mv = Diff('x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

        for i in np.random.rand(30):
            mv.push(dict(x=float(i)))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

    def testSimpleReturn(self):
        mm = SimpleReturn('close')
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
        mm = LogReturn('close')
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
        mm = Sum('close')

        for i, value in enumerate(self.samplesClose):
            mm.push(dict(close=value))
            expected = np.sum(self.samplesClose[:i + 1])
            calculated = mm.result()

            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected sum:   {1:f}\n"
                                                             "calculated sum: {2:f}".format(i, expected, calculated))

    def testVariance(self):
        # np.var is population variance
        mm = Variance('close', isPopulation=True)
        mm2 = Variance('close', )

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

    def testProduct(self):
        product = Product('close')
        expected = 1
        for i, value in enumerate(self.samplesClose):
            product.push(dict(close=value))
            calculated = product.result()
            expected *= value
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected product:   {1:f}\n"
                                                             "calculated product: {2:f}".format(i, expected,
                                                                                                calculated))


if __name__ == '__main__':
    unittest.main()
