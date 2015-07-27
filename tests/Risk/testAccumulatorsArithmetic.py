# -*- coding: utf-8 -*-
u"""
Created on 2015-7-27

@author: cheng.li
"""

import unittest
import numpy as np
from finpy.Risk.StatefulAccumulators import MovingAverage
from finpy.Risk.StatelessAccumulators import Sum


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
        plusRes = MovingAverage(5, 'close') -Sum('open')

        sampleOpen = np.random.randn(10000)
        sampleClose = np.random.randn(10000)

        for i, (open, close) in enumerate(zip(sampleOpen, sampleClose)):
            ma5.push(close=close)
            sumTotal.push(open=open)
            plusRes.push(open=open, close=close)

            expected = ma5.result() - sumTotal.result()
            calculated = plusRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))