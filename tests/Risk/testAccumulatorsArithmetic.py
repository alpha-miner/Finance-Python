# -*- coding: utf-8 -*-
u"""
Created on 2015-7-27

@author: cheng.li
"""

import unittest
import numpy as np
from finpy.Risk.StatefulAccumulators import MovingAverage
from finpy.Risk.StatefulAccumulators import MovingVariance
from finpy.Risk.StatefulAccumulators import MovingMax
from finpy.Risk.StatefulAccumulators import MovingCorrelation
from finpy.Risk.StatelessAccumulators import Sum
from finpy.Risk.StatelessAccumulators import Average
from finpy.Risk.StatelessAccumulators import Minum
from finpy.Risk.StatelessAccumulators import Max


class TestAccumulatorsArithmetic(unittest.TestCase):

    def testPlusOperator(self):
        ma5 = MovingAverage(5, 'close')
        ma20 = MovingAverage(20, 'open')
        plusRes = MovingAverage(5, 'close') + MovingAverage(20, 'open')

        sampleOpen = np.random.randn(10000)
        sampleClose = np.random.randn(10000)

        for i, (open, close) in enumerate(zip(sampleOpen, sampleClose)):
            ma5.push(close=close)
            ma20.push(open=open)
            plusRes.push(open=open, close=close)

            expected = ma5.result() + ma20.result()
            calculated = plusRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testSubOperator(self):
        ma5 = MovingAverage(5, 'close')
        sumTotal = Sum('open')
        subRes = MovingAverage(5, 'close') - Sum('open')

        sampleOpen = np.random.randn(10000)
        sampleClose = np.random.randn(10000)

        for i, (open, close) in enumerate(zip(sampleOpen, sampleClose)):
            ma5.push(close=close)
            sumTotal.push(open=open)
            subRes.push(open=open, close=close)

            expected = ma5.result() - sumTotal.result()
            calculated = subRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testMultiplyOperator(self):
        mv5 = MovingVariance(5, 'close')
        average = Average('open')
        mulRes = MovingVariance(5, 'close') * Average('open')

        sampleOpen = np.random.randn(10000)
        sampleClose = np.random.randn(10000)

        for i, (open, close) in enumerate(zip(sampleOpen, sampleClose)):
            mv5.push(close=close)
            average.push(open=open)
            mulRes.push(open=open, close=close)

            if i >= 1:
                expected = mv5.result() * average.result()
                calculated = mulRes.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

    def testDivOperator(self):
        mc5 = MovingCorrelation(5, ['open', 'close'])
        minum = Minum('open')
        divRes = Minum('open') / MovingCorrelation(5, ['open', 'close'])

        sampleOpen = np.random.randn(10000)
        sampleClose = np.random.randn(10000)

        for i, (open, close) in enumerate(zip(sampleOpen, sampleClose)):
            mc5.push(open=open, close=close)
            minum.push(open=open)
            divRes.push(open=open, close=close)

            if i >= 1:
                expected = minum.result() / mc5.result()
                calculated = divRes.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

    def testMultipleOperators(self):
        ma20 = MovingAverage(20, 'close')
        ma120 = MovingAverage(120, 'close')
        mmax = MovingMax(50, 'open')
        res = (MovingAverage(20, 'close') - MovingAverage(120, 'close')) / MovingMax(50, 'open')

        sampleOpen = np.random.randn(10000)
        sampleClose = np.random.randn(10000)

        for i, (open, close) in enumerate(zip(sampleOpen, sampleClose)):
            ma20.push(close=close)
            ma120.push(close=close)
            mmax.push(open=open)
            res.push(open=open, close=close)

            expected = (ma20.result() - ma120.result()) / mmax.result()
            calculated = res.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testCompoundedOperator(self):
        ma5 = MovingAverage(5, 'close')
        maxer = Max('x')
        max5ma = MovingAverage(5, 'close') >> Max()

        sample = np.random.randn(10000)

        for i, close in enumerate(sample):
            ma5.push(close=close)
            maxer.push(x=ma5.result())
            max5ma.push(close=close)

            expected = maxer.result()
            calculated = max5ma.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))