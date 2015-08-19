# -*- coding: utf-8 -*-
u"""
Created on 2015-7-27

@author: cheng.li
"""

import unittest
import math
from collections import deque
import numpy as np
from scipy.stats import linregress
from PyFin.Math.Accumulators.IAccumulators import Exp
from PyFin.Math.Accumulators.IAccumulators import Log
from PyFin.Math.Accumulators.IAccumulators import Sqrt
from PyFin.Math.Accumulators.IAccumulators import Abs
from PyFin.Math.Accumulators.IAccumulators import Pow
from PyFin.Math.Accumulators.IAccumulators import Acos
from PyFin.Math.Accumulators.IAccumulators import Acosh
from PyFin.Math.Accumulators.IAccumulators import Asin
from PyFin.Math.Accumulators.IAccumulators import Asinh
from PyFin.Math.Accumulators.IAccumulators import TruncatedValueHolder
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingVariance
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMax
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCorrelation
from PyFin.Math.Accumulators.StatelessAccumulators import Sum
from PyFin.Math.Accumulators.StatelessAccumulators import Average
from PyFin.Math.Accumulators.StatelessAccumulators import Minimum
from PyFin.Math.Accumulators.StatelessAccumulators import Max
from PyFin.Math.Accumulators.StatelessAccumulators import Correlation
from PyFin.Math.Accumulators.Performancers import MovingAlphaBeta


class TestAccumulatorsArithmetic(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.sampleOpen = np.random.randn(10000)
        self.sampleClose = np.random.randn(10000)
        self.sampleRf = np.random.randn(10000)

    def testAccumulatorBasic(self):

        # check parameter list should not be empty
        with self.assertRaises(ValueError):
            Max(dependency=[])

        m = Max(dependency='x')
        m.push({'x': 10.0})
        self.assertAlmostEqual(m.result(), m.value)

    def testPlusOperator(self):
        ma5 = MovingAverage(5, 'close')
        ma20 = MovingAverage(20, 'open')
        plusRes = ma5 + ma20
        concated = (ma5 ^ ma20) + 2.0
        concated2 = ma5 + (ma5 ^ ma20)

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma5.push(data)
            ma20.push(data)
            plusRes.push(data)
            concated.push(data)
            concated2.push(data)

            expected = ma5.result() + ma20.result()
            calculated = plusRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            expected = (ma5.result() + 2.0, ma20.result() + 2.0)
            calculated = concated.result()
            self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[0],
                                                                                              calculated[0]))
            self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[1],
                                                                                              calculated[1]))

            expected = (ma5.result() + ma5.result(), ma20.result() + ma5.result())
            calculated = concated2.result()
            self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[0],
                                                                                              calculated[0]))
            self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[1],
                                                                                              calculated[1]))

    def testRPlusOperator(self):
        ma5 = MovingAverage(5, 'close')
        ma20 = MovingAverage(20, 'close')
        plusRes = 5.0 + MovingAverage(20, 'close')
        concated = 2.0 + (ma5 ^ ma20)
        concated2 = ma5 + ma20
        concated3 = (ma5 ^ ma20) + ma5

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            ma20.push(data)
            plusRes.push(data)
            concated.push(data)
            concated2.push(data)
            concated3.push(data)

            expected = 5.0 + ma20.result()
            calculated = plusRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            expected = (ma5.result() + 2.0, ma20.result() + 2.0)
            calculated = concated.result()
            self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[0],
                                                                                              calculated[0]))
            self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[1],
                                                                                              calculated[1]))

            expected = ma5.result() + ma20.result()
            calculated = concated2.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            expected = (ma5.result() + ma5.result(), ma5.result() + ma20.result())
            calculated = concated3.result()
            self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[0],
                                                                                              calculated[0]))
            self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[1],
                                                                                              calculated[1]))

    def testSubOperator(self):
        ma5 = MovingAverage(5, 'close')
        sumTotal = Sum('open')
        subRes = MovingAverage(5, 'close') - Sum('open')
        concated = (MovingAverage(5, 'close') ^ Sum('open')) - Sum('open')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma5.push(data)
            sumTotal.push(data)
            subRes.push(data)
            concated.push(data)

            expected = ma5.result() - sumTotal.result()
            calculated = subRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            expected = (ma5.result() - sumTotal.result(), 0.0)
            calculated = concated.result()
            self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[0],
                                                                                              calculated[0]))
            self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[1],
                                                                                              calculated[1]))

    def testRSubOperator(self):
        ma20 = MovingAverage(20, 'close')
        sumTotal = Sum('close')
        subRes = 5.0 - MovingAverage(20, 'close')
        concated = sumTotal - (ma20 ^ sumTotal)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma20.push(data)
            sumTotal.push(data)
            subRes.push(data)
            concated.push(data)

            expected = 5.0 - ma20.result()
            calculated = subRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            expected = (sumTotal.result() - ma20.result(), 0.0)
            calculated = concated.result()
            self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[0],
                                                                                              calculated[0]))
            self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[1],
                                                                                              calculated[1]))

    def testMultiplyOperator(self):
        mv5 = MovingVariance(5, 'close')
        average = Average('open')
        mulRes = MovingVariance(5, 'close') * Average('open')
        concated = (Average('open') ^ mv5) * Average('open')
        concated2 = Average('open') * (Average('open') ^ mv5)

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            mv5.push(data)
            average.push(data)
            mulRes.push(data)
            concated.push(data)
            concated2.push(data)

            if i >= 1:
                expected = mv5.result() * average.result()
                calculated = mulRes.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

                expected = (average.result() * average.result(), mv5.result() * average.result())
                calculated = concated.result()
                self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                       "expected:   {1:f}\n"
                                                                       "calculated: {2:f}".format(i, expected[0],
                                                                                                  calculated[0]))
                self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                       "expected:   {1:f}\n"
                                                                       "calculated: {2:f}".format(i, expected[1],
                                                                                                  calculated[1]))

                calculated = concated2.result()
                self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                       "expected:   {1:f}\n"
                                                                       "calculated: {2:f}".format(i, expected[0],
                                                                                                  calculated[0]))
                self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                       "expected:   {1:f}\n"
                                                                       "calculated: {2:f}".format(i, expected[1],
                                                                                                  calculated[1]))

    def testRMultiplyOperator(self):
        ma20 = MovingAverage(20, 'close')
        average = Average('open')
        mulRes = 5.0 * MovingAverage(20, 'close')
        concated = 5.0 * (MovingAverage(20, 'close') ^ Average('open'))

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            average.push(data)
            ma20.push(data)
            mulRes.push(data)
            concated.push(data)

            expected = 5.0 * ma20.result()
            calculated = mulRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            expected = (5.0 * ma20.result(), 5.0 * average.result())
            calculated = concated.result()
            self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[0],
                                                                                              calculated[0]))
            self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[1],
                                                                                              calculated[1]))

    def testDivOperator(self):
        mc5 = MovingCorrelation(5, ['open', 'close'])
        minum = Minimum('open')
        divRes = Minimum('open') / MovingCorrelation(5, ['open', 'close'])
        concated = (Minimum('open') ^ MovingCorrelation(5, ['open', 'close'])) / MovingCorrelation(5, ['open', 'close'])
        concated2 = MovingCorrelation(5, ['open', 'close']) / (
        Minimum('open') ^ MovingCorrelation(5, ['open', 'close']))

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            mc5.push(data)
            minum.push(data)
            divRes.push(data)
            concated.push(data)
            concated2.push(data)

            if i >= 1:
                expected = minum.result() / mc5.result()
                calculated = divRes.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

                expected = (minum.result() / mc5.result(), mc5.result() / mc5.result())
                calculated = concated.result()
                self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                       "expected:   {1:f}\n"
                                                                       "calculated: {2:f}".format(i, expected[0],
                                                                                                  calculated[0]))
                self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                       "expected:   {1:f}\n"
                                                                       "calculated: {2:f}".format(i, expected[1],
                                                                                                  calculated[1]))

                expected = (mc5.result() / minum.result(), mc5.result() / mc5.result())
                calculated = concated2.result()
                self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                       "expected:   {1:f}\n"
                                                                       "calculated: {2:f}".format(i, expected[0],
                                                                                                  calculated[0]))
                self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                       "expected:   {1:f}\n"
                                                                       "calculated: {2:f}".format(i, expected[1],
                                                                                                  calculated[1]))

    def testRDivOperator(self):
        ma20 = MovingAverage(20, 'close')
        divRes = 5.0 / MovingAverage(20, 'close')
        concated = (5.0 ^ MovingAverage(20, 'close')) / MovingAverage(20, 'close')

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma20.push(data)
            divRes.push(data)
            concated.push(data)

            expected = 5.0 / ma20.result()
            calculated = divRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            expected = (5.0 / ma20.result(), 1.0)
            calculated = concated.result()
            self.assertAlmostEqual(calculated[0], expected[0], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[0],
                                                                                              calculated[0]))
            self.assertAlmostEqual(calculated[1], expected[1], 12, "at index {0:d}\n"
                                                                   "expected:   {1:f}\n"
                                                                   "calculated: {2:f}".format(i, expected[1],
                                                                                              calculated[1]))

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
        negma20square = -(ma20 ^ ma20)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma20.push(data)
            negma20.push(data)
            negma20square.push(data)

            expected = -ma20.result()
            calculated = negma20.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            calculated = negma20square.result()
            for cal in calculated:
                self.assertAlmostEqual(cal, expected, 12, "at index {0:d}\n"
                                                          "expected:   {1:f}\n"
                                                          "calculated: {2:f}".format(i, expected, cal))

    def testListedOperator(self):
        ma20 = MovingAverage(20, 'close')
        maxer = Max('open')
        minimumer = Minimum('close')
        listHolder = MovingAverage(20, 'close') ^ Max('open') ^ Minimum('close')
        listHolder2 = 2.0 ^ MovingAverage(20, 'close')
        listHolder3 = MovingAverage(20, 'close') ^ 2.0

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma20.push(data)
            maxer.push(data)
            minimumer.push(data)
            listHolder.push(data)
            listHolder2.push(data)
            listHolder3.push(data)

            expected = (ma20.result(), maxer.result(), minimumer.result())
            calculated = listHolder.result()
            for ev, cv in zip(expected, calculated):
                self.assertAlmostEqual(ev, cv, 12, "at index {0:d}\n"
                                                   "expected:   {1}\n"
                                                   "calculated: {2}".format(i, expected, calculated))

            expected = (2.0, ma20.result())
            calculated = listHolder2.result()
            for ev, cv in zip(expected, calculated):
                self.assertAlmostEqual(ev, cv, 12, "at index {0:d}\n"
                                                   "expected:   {1}\n"
                                                   "calculated: {2}".format(i, expected, calculated))

            expected = (ma20.result(), 2.0)
            calculated = listHolder3.result()
            for ev, cv in zip(expected, calculated):
                self.assertAlmostEqual(ev, cv, 12, "at index {0:d}\n"
                                                   "expected:   {1}\n"
                                                   "calculated: {2}".format(i, expected, calculated))

    def testCompoundedOperator(self):
        ma5 = MovingAverage(5, 'x')
        maxer = Max('close')
        max5ma = Max('close') >> MovingAverage(5)
        max5ma2 = MovingAverage(5, Max('close'))
        average = Average('close')
        sumM = Sum('close')
        mvTest = Correlation(dependency=('x', 'y'))
        mvCorr = (Average('close') ^ Sum('close')) >> Correlation(dependency=('x', 'y'))

        for i, close in enumerate(self.sampleClose):
            data = {'close': close, 'open': open}
            maxer.push(data)
            data2 = {'x': maxer.result()}
            ma5.push(data2)
            max5ma.push(data)
            max5ma2.push(data)
            average.push(data)
            sumM.push(data)
            data3 = {'x': average.result(), 'y': sumM.result()}
            mvTest.push(data3)
            mvCorr.push(data)

            expected = ma5.result()
            calculated = max5ma.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            calculated = max5ma2.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            if i >= 1:
                expected = mvTest.result()
                calculated = mvCorr.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = Max('close') >> math.sqrt

        with self.assertRaises(ValueError):
            _ = (Max('close') ^ Minimum('close')) >> MovingCorrelation(20, dependency=('x', 'y', 'z'))

        (Max('close') ^ Minimum('close')) >> MovingCorrelation(20, dependency=('x', 'y'))

    def testListedAndCompoundedOperator(self):
        maClose = MovingAverage(20, 'close')
        maOpen = MovingAverage(10, 'open')
        maRf = MovingAverage(10, 'rf')
        listHolder = MovingAverage(20, 'close') ^ MovingAverage(10, 'open') ^ MovingAverage(10, 'rf')
        mc = MovingAlphaBeta(20, listHolder)

        maCloseContainer = deque(maxlen=20)
        maOpenContainer = deque(maxlen=20)

        for i, (open, close, rf) in enumerate(zip(self.sampleOpen, self.sampleClose, self.sampleRf)):
            data = {'close': close, 'open': open, 'rf': rf}
            maClose.push(data)
            maOpen.push(data)
            maRf.push(data)
            mc.push(data)
            maCloseContainer.append(maClose.result() - maRf.result())
            maOpenContainer.append(maOpen.result() - maRf.result())

            if i >= 2:
                expected = linregress(maOpenContainer, maCloseContainer)
                calculated = mc.result()

                # check alpha
                self.assertAlmostEqual(expected[1], calculated[0], 10, "at index {0:d}\n"
                                                                       "expected alpha:   {1:f}\n"
                                                                       "calculated alpha: {2:f}".format(i, expected[1],
                                                                                                        calculated[0]))

                # check beta
                self.assertAlmostEqual(expected[0], calculated[1], 10, "at index {0:d}\n"
                                                                       "expected beta:   {1:f}\n"
                                                                       "calculated beta: {2:f}".format(i, expected[0],
                                                                                                       calculated[1]))

    def testTruncatedValueHolder(self):
        ma20 = MovingAverage(20, 'close')
        max5 = MovingMax(5, 'open')

        with self.assertRaises(TypeError):
            _ = TruncatedValueHolder(ma20, 1)

        test = TruncatedValueHolder(ma20 ^ max5, 1)
        test.push(dict(close=10.0, open=5.0))
        test.push(dict(close=10.0, open=20.0))
        self.assertAlmostEqual(test.result(), 20.0, 15)

        test = TruncatedValueHolder(ma20 ^ max5, 0)
        test.push(dict(close=10.0, open=5.0))
        test.push(dict(close=15.0, open=20.0))
        self.assertAlmostEqual(test.result(), 12.50, 15)

        test = TruncatedValueHolder(ma20 ^ max5, slice(1, 2))
        test.push(dict(close=10.0, open=5.0))
        test.push(dict(close=15.0, open=20.0))
        self.assertAlmostEqual(test.result(), (20.0,), 15)

        test = TruncatedValueHolder(ma20 ^ max5, slice(0, -1))
        test.push(dict(close=10.0, open=5.0))
        test.push(dict(close=15.0, open=20.0))
        self.assertAlmostEqual(test.result(), (12.5,), 15)

        with self.assertRaises(ValueError):
            _ = TruncatedValueHolder(ma20 ^ max5, slice(1, -2))

    def testGetItemOperator(self):
        listHolder = MovingAverage(20, 'close') ^ Max('open') ^ Minimum('close')
        listHolder1 = listHolder[1]
        listHolder2 = listHolder[1:3]
        maxer = Max('open')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            listHolder1.push(data)
            listHolder2.push(data)
            maxer.push(data)

            expected = maxer.result()
            calculated = listHolder1.result()
            self.assertAlmostEqual(expected, calculated, 12, "at index {0:d}\n"
                                                             "expected beta:   {1:f}\n"
                                                             "calculated beta: {2:f}".format(i, expected, calculated))

            calculated = listHolder2.result()[0]
            self.assertAlmostEqual(expected, calculated, 12, "at index {0:d}\n"
                                                             "expected beta:   {1:f}\n"
                                                             "calculated beta: {2:f}".format(i, expected, calculated))

    def testLessOrEqualOperators(self):
        m1 = Max('x')
        m2 = Minimum('x')
        cmp = m1 <= m2

        cmp.push(dict(x=1.0))
        self.assertEqual(True, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(False, cmp.result())

        cmp = (m1 ^ m2) <= m2
        cmp.push(dict(x=1.0))
        self.assertEqual((True, True), cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual((False, True), cmp.result())

        cmp = m1 <= (m1 ^ m2)
        cmp.push(dict(x=1.0))
        self.assertEqual((True, True), cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual((True, False), cmp.result())

    def testLessOperator(self):
        m1 = Minimum('x')
        m2 = Max('x')
        cmp = m1 < m2

        cmp.push(dict(x=1.0))
        self.assertEqual(False, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(True, cmp.result())

        cmp = (m1 ^ m2) < m2
        cmp.push(dict(x=1.0))
        self.assertEqual((False, False), cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual((True, False), cmp.result())

        cmp = m1 < (m1 ^ m2)
        cmp.push(dict(x=1.0))
        self.assertEqual((False, False), cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual((False, True), cmp.result())

    def testGreaterOrEqualOperator(self):
        m1 = Minimum('x')
        m2 = Max('x')
        cmp = m1 >= m2

        cmp.push(dict(x=1.0))
        self.assertEqual(True, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(False, cmp.result())

        cmp = (m1 ^ m2) >= m2
        cmp.push(dict(x=1.0))
        self.assertEqual((True, True), cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual((False, True), cmp.result())

        cmp = m1 >= (m1 ^ m2)
        cmp.push(dict(x=1.0))
        self.assertEqual((True, True), cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual((True, False), cmp.result())

    def testGreaterOperator(self):
        m1 = Max('x')
        m2 = Minimum('x')
        cmp = m1 > m2

        cmp.push(dict(x=1.0))
        self.assertEqual(False, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(True, cmp.result())

        cmp = (m1 ^ m2) > m2
        cmp.push(dict(x=1.0))
        self.assertEqual((False, False), cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual((True, False), cmp.result())

        cmp = m1 > (m1 ^ m2)
        cmp.push(dict(x=1.0))
        self.assertEqual((False, False), cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual((False, True), cmp.result())

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
        holder2 = (ma5 ^ ma5) >> Log

        sampleClose = np.exp(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)
            holder2.push(data)

            expected = math.log(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            calculated = holder2.result()
            for cal in calculated:
                self.assertAlmostEqual(cal, expected, 12, "at index {0:d}\n"
                                                          "expected:   {1:f}\n"
                                                          "calculated: {2:f}".format(i, expected, cal))

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
        ma5min = MovingAverage(5, 'close') >> Minimum
        holder = Pow(ma5min, 3)
        holder2 = Pow(ma5min ^ ma5min, 3)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5min.push(data)
            holder.push(data)
            holder2.push(data)

            expected = math.pow(ma5min.result(), 3)
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            calculated = holder2.result()
            for cal in calculated:
                self.assertAlmostEqual(cal, expected, 12, "at index {0:d}\n"
                                                          "expected:   {1:f}\n"
                                                          "calculated: {2:f}".format(i, expected, cal))

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

        sampleClose = np.sinh(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.asinh(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))
