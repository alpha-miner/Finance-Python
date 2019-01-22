# -*- coding: utf-8 -*-
u"""
Created on 2015-7-27

@author: cheng.li
"""

import unittest
import copy
import tempfile
import pickle
import os
import math
import numpy as np
import pandas as pd
from scipy.stats import norm
from PyFin.Math.Accumulators.IAccumulators import Identity
from PyFin.Math.Accumulators.IAccumulators import Exp
from PyFin.Math.Accumulators.IAccumulators import Log
from PyFin.Math.Accumulators.IAccumulators import Sqrt
from PyFin.Math.Accumulators.IAccumulators import Sign
from PyFin.Math.Accumulators.IAccumulators import Abs
from PyFin.Math.Accumulators.IAccumulators import Pow
from PyFin.Math.Accumulators.IAccumulators import Acos
from PyFin.Math.Accumulators.IAccumulators import Acosh
from PyFin.Math.Accumulators.IAccumulators import Asin
from PyFin.Math.Accumulators.IAccumulators import Asinh
from PyFin.Math.Accumulators.IAccumulators import NormInv
from PyFin.Math.Accumulators.IAccumulators import IIF
from PyFin.Math.Accumulators.IAccumulators import Latest
from PyFin.Math.Accumulators.IAccumulators import Ceil
from PyFin.Math.Accumulators.IAccumulators import Floor
from PyFin.Math.Accumulators.IAccumulators import Round
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingVariance
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMax
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCorrelation
from PyFin.Math.Accumulators.StatelessAccumulators import Sum
from PyFin.Math.Accumulators.StatelessAccumulators import Average
from PyFin.Math.Accumulators.StatelessAccumulators import Min
from PyFin.Math.Accumulators.StatelessAccumulators import Max


class TestAccumulatorsArithmetic(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.sampleOpen = np.random.randn(10000)
        self.sampleClose = np.random.randn(10000)
        self.sampleRf = np.random.randn(10000)

    def testAddedNanValue(self):
        m = Max('x')
        m.push({'x': 10.0})
        m.push({'x': np.nan})
        self.assertAlmostEqual(10., m.value)

    def testAccumulatorBasic(self):
        m = Max('x')
        m.push({'x': 10.0})
        self.assertAlmostEqual(m.result(), m.value)

    def testPlusOperator(self):
        ma5 = MovingAverage(5, 'close')
        ma20 = MovingAverage(20, 'open')
        plusRes = ma5 + ma20

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma5.push(data)
            ma20.push(data)
            plusRes.push(data)

            expected = ma5.result() + ma20.result()
            calculated = plusRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testRPlusOperator(self):
        ma5 = MovingAverage(5, 'close')
        ma20 = MovingAverage(20, 'close')
        plusRes = 5.0 + MovingAverage(20, 'close')

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            ma20.push(data)
            plusRes.push(data)
            expected = 5.0 + ma20.result()
            calculated = plusRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testSubOperator(self):
        ma5 = MovingAverage(5, 'close')
        sumTotal = Sum('open')
        subRes = MovingAverage(5, 'close') - Sum('open')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma5.push(data)
            sumTotal.push(data)
            subRes.push(data)

            expected = ma5.result() - sumTotal.result()
            calculated = subRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testRSubOperator(self):
        ma20 = MovingAverage(20, 'close')
        sumTotal = Sum('close')
        subRes = 5.0 - MovingAverage(20, 'close')

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma20.push(data)
            sumTotal.push(data)
            subRes.push(data)

            expected = 5.0 - ma20.result()
            calculated = subRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testMultiplyOperator(self):
        mv5 = MovingVariance(5, 'close')
        average = Average('open')
        mulRes = MovingVariance(5, 'close') * Average('open')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            mv5.push(data)
            average.push(data)
            mulRes.push(data)

            if i >= 1:
                expected = mv5.result() * average.result()
                calculated = mulRes.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

    def testRMultiplyOperator(self):
        ma20 = MovingAverage(20, 'close')
        average = Average('open')
        mulRes = 5.0 * MovingAverage(20, 'close')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            average.push(data)
            ma20.push(data)
            mulRes.push(data)

            expected = 5.0 * ma20.result()
            calculated = mulRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testDivOperator(self):
        mc5 = MovingCorrelation(5, 'open', 'close')
        minum = Min('open')
        divRes = Min('open') / MovingCorrelation(5, 'open', 'close')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            mc5.push(data)
            minum.push(data)
            divRes.push(data)

            if i >= 1:
                expected = minum.result() / mc5.result()
                calculated = divRes.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

    def testRDivOperator(self):
        ma20 = MovingAverage(20, 'close')
        divRes = 5.0 / MovingAverage(20, 'close')

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma20.push(data)
            divRes.push(data)

            expected = 5.0 / ma20.result()
            calculated = divRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testMultipleOperators(self):
        ma20 = MovingAverage(20, 'close')
        ma120 = MovingAverage(120, 'close')
        mmax = MovingMax(50, 'open')
        res = (MovingAverage(20, 'close') - MovingAverage(120, 'close')) / MovingMax(50, 'open')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma20.push(data)
            ma120.push(data)
            mmax.push(data)
            res.push(data)

            expected = (ma20.result() - ma120.result()) / mmax.result()
            calculated = res.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testNegativeOperator(self):
        ma20 = MovingAverage(20, 'close')
        negma20 = -ma20

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma20.push(data)
            negma20.push(data)

            expected = -ma20.result()
            calculated = negma20.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testCompoundedOperator(self):
        ma5 = MovingAverage(5, 'x')
        maxer = Max('close')
        max5ma = Max('close') >> MovingAverage(5, 'max')
        max5ma2 = MovingAverage(5, Max('close'))

        for i, close in enumerate(self.sampleClose):
            data = {'close': close, 'open': 1.}
            maxer.push(data)
            data2 = {'x': maxer.result()}
            ma5.push(data2)
            max5ma.push(data)
            max5ma2.push(data)

            expected = ma5.result()
            calculated = max5ma.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            calculated = max5ma2.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = Max('close') >> math.sqrt

    def testLessOrEqualOperators(self):
        m1 = Max('x')
        m2 = Min('x')
        cmp = m1 <= m2

        cmp.push(dict(x=1.0))
        self.assertEqual(True, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(False, cmp.result())

    def testLessOperator(self):
        m1 = Min('x')
        m2 = Max('x')
        cmp = m1 < m2

        cmp.push(dict(x=1.0))
        self.assertEqual(False, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(True, cmp.result())

    def testGreaterOrEqualOperator(self):
        m1 = Min('x')
        m2 = Max('x')
        cmp = m1 >= m2

        cmp.push(dict(x=1.0))
        self.assertEqual(True, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(False, cmp.result())

    def testGreaterOperator(self):
        m1 = Max('x')
        m2 = Min('x')
        cmp = m1 > m2

        cmp.push(dict(x=1.0))
        self.assertEqual(False, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(True, cmp.result())

    def testExpFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Exp(MovingAverage(5, 'close'))
        holder2 = MovingAverage(5, 'close') >> Exp

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)
            holder2.push(data)

            expected = math.exp(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            calculated = holder2.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testLogFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Log(ma5)
        sampleClose = np.exp(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.log(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testSignFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Sign(ma5)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = 1 if ma5.result() >= 0 else -1
            calculated = holder.result()

            self.assertEqual(calculated, expected, "at index {0:d}\n"
                                                   "expected:   {1:f}\n"
                                                   "calculated: {2:f}".format(i, expected, calculated))

    def testSqrtFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Sqrt(ma5)

        sampleClose = np.square(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.sqrt(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAbsFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Abs(ma5)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = abs(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testPowFunction(self):
        ma5min = MovingAverage(5, 'close') >> Min
        holder = Pow(ma5min, 3)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5min.push(data)
            holder.push(data)

            expected = math.pow(ma5min.result(), 3)
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAcosFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Acos(ma5)

        sampleClose = np.cos(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.acos(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAcoshFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Acosh(ma5)

        sampleClose = np.cosh(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.acosh(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAsinFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Asin(ma5)

        sampleClose = np.sin(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.asin(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAsinhFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Asinh(ma5)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.asinh(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testNormInvFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = NormInv(ma5)

        sampleClose = norm.cdf(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = norm.ppf(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 6, "at index {0:d}\n"
                                                            "expected:   {1:f}\n"
                                                            "calculated: {2:f}".format(i, expected, calculated))

        holder = NormInv(ma5, fullAcc=True)
        sampleClose = norm.cdf(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = norm.ppf(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testCeilFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Ceil(ma5)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.ceil(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testFloorFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Floor(ma5)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.floor(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testRoundFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Round(ma5)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = round(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testArithmeticFunctionsDeepcopy(self):
        data = {'x': 1}

        test = Exp('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.exp(data['x']), copied.value)

        test = Log('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.log(data['x']), copied.value)

        test = Sqrt('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.sqrt(data['x']), copied.value)

        data['x'] = -1.

        test = Pow('x', 2)
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(data['x'] ** 2, copied.value)

        test = Abs('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(abs(data['x']), copied.value)

        test = Sign('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(-1., copied.value)

        data['x'] = 1.

        test = Acos('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.acos(data['x']), copied.value)

        test = Asin('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.asin(data['x']), copied.value)

        test = Acosh('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.acosh(data['x']), copied.value)

        test = Asinh('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.asinh(data['x']), copied.value)

    def testArithmeticFunctionsPickle(self):
        data = {'x': 1}

        test = Exp('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Log('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Sqrt('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        data['x'] = -1.

        test = Pow('x', 2)
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Abs('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Sign('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        data['x'] = 1.

        test = Acos('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Asin('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Acosh('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Asinh('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testAccumulatorTransform(self):
        window = 5
        ma5 = MovingAverage(window, 'close')
        df = pd.DataFrame(self.sampleClose, columns=['close'])
        res = ma5.transform(df, name='my_factor')[window-1:]
        expected = df.rolling(window).mean()[window - 1:]['close']

        self.assertEqual(res.name, 'my_factor')
        np.testing.assert_array_almost_equal(res, expected)

    def testIIFAccumulator(self):
        iif = IIF(Latest('rf') > 0, 'close', 'open')

        for i, close in enumerate(self.sampleClose):
            data = {'close': close,
                    'open': self.sampleOpen[i],
                    'rf': self.sampleRf[i]}

            iif.push(data)

            if data['rf'] > 0:
                self.assertAlmostEqual(iif.result(), data['close'])
            else:
                self.assertAlmostEqual(iif.result(), data['open'])

    def testIdentityStr(self):
        s = Identity(2.)
        self.assertEqual('2.0', str(s))

    def testLatestStr(self):
        s = Latest('roe')
        self.assertEqual("''\\text{roe}''", str(s))

    def testExpStr(self):
        s = Exp('roe')
        self.assertEqual("\exp(''\\text{roe}'')", str(s))

    def testLogStr(self):
        s = Log('roe')
        self.assertEqual("\ln(''\\text{roe}'')", str(s))

    def testSqrtStr(self):
        s = Sqrt('roe')
        self.assertEqual("\sqrt{''\\text{roe}''}", str(s))

    def testPowStr(self):
        s = Pow('roe', 3)
        self.assertEqual("''\\text{roe}'' ^ {3.0}", str(s))

    def testAbsStr(self):
        s = Abs('roe')
        self.assertEqual("\\left| ''\\text{roe}'' \\right|", str(s))

    def testSignStr(self):
        s = Sign('roe')
        self.assertEqual("\mathrm{sign}(''\\text{roe}'')", str(s))

    def testAcosStr(self):
        s = Acos('roe')
        self.assertEqual("\mathrm{ACos}(''\\text{roe}'')", str(s))

    def testAcoshStr(self):
        s = Acosh('roe')
        self.assertEqual("\mathrm{ACosh}(''\\text{roe}'')", str(s))

    def testAsinStr(self):
        s = Asin('roe')
        self.assertEqual("\mathrm{ASin}(''\\text{roe}'')", str(s))

    def testAsinhStr(self):
        s = Asinh('roe')
        self.assertEqual("\mathrm{ASinh}(''\\text{roe}'')", str(s))

    def testNormInvStr(self):
        s = NormInv('roe')
        self.assertEqual("\mathrm{NormInv}(''\\text{roe}'', fullAcc=0)", str(s))

    def testNegStr(self):
        s = -Asinh('roe')
        self.assertEqual("-\mathrm{ASinh}(''\\text{roe}'')", str(s))

    def testAddedStr(self):
        s = Latest('x') + Latest('y')
        self.assertEqual("''\\text{x}'' + ''\\text{y}''", str(s))

    def testMinusStr(self):
        s = Latest('x') - Latest('y')
        self.assertEqual("''\\text{x}'' - ''\\text{y}''", str(s))

    def testMultiplyStr(self):
        s = Latest('x') * Latest('y')
        self.assertEqual("''\\text{x}'' \\times ''\\text{y}''", str(s))

        s = (Latest('x') + Latest('y')) * (Latest('x') - Latest('y'))
        self.assertEqual("(''\\text{x}'' + ''\\text{y}'') \\times (''\\text{x}'' - ''\\text{y}'')", str(s))

    def testDividedStr(self):
        s = (Latest('x') + Latest('y')) / (Latest('x') - Latest('y'))
        self.assertEqual("\\frac{''\\text{x}'' + ''\\text{y}''}{''\\text{x}'' - ''\\text{y}''}", str(s))

    def testLtOperatorStr(self):
        s = (Latest('x') + Latest('y')) < (Latest('x') - Latest('y'))
        self.assertEqual("(''\\text{x}'' + ''\\text{y}'') \lt (''\\text{x}'' - ''\\text{y}'')", str(s))

    def testLeOperatorStr(self):
        s = (Latest('x') * Latest('y')) <= (Latest('x') - Latest('y'))
        self.assertEqual("(''\\text{x}'' \\times ''\\text{y}'') \le (''\\text{x}'' - ''\\text{y}'')", str(s))

    def testGeOperatorStr(self):
        s = (Latest('x') * Latest('y')) >= (Latest('x') - Latest('y'))
        self.assertEqual("(''\\text{x}'' \\times ''\\text{y}'') \ge (''\\text{x}'' - ''\\text{y}'')", str(s))

    def testGtOperatorStr(self):
        s = (Latest('x') * Latest('y')) > (Latest('x') - Latest('y'))
        self.assertEqual("(''\\text{x}'' \\times ''\\text{y}'') \gt (''\\text{x}'' - ''\\text{y}'')", str(s))

    def testEqOperatorStr(self):
        s = (Latest('x') * Latest('y')) == (Latest('x') - Latest('y'))
        self.assertEqual("(''\\text{x}'' \\times ''\\text{y}'') = (''\\text{x}'' - ''\\text{y}'')", str(s))

    def testNeqOperatorStr(self):
        s = (Latest('x') * Latest('y')) != (Latest('x') - Latest('y'))
        self.assertEqual("(''\\text{x}'' \\times ''\\text{y}'') \\neq (''\\text{x}'' - ''\\text{y}'')", str(s))
