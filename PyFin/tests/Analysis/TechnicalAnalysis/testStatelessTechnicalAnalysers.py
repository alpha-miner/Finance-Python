# -*- coding: utf-8 -*-
u"""
Created on 2016-1-13

@author: cheng.li
"""

import unittest
import numpy as np
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityXAverageValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityMACDValueHolder


class TestStatelessTechnicalAnalysis(unittest.TestCase):

    def setUp(self):
        # preparing market data
        np.random.seed(0)
        aaplClose = np.random.randn(1000)
        aaplOpen = np.random.randn(1000)
        self.aapl = {'close': aaplClose, 'open': aaplOpen}

        ibmClose = np.random.randn(1000)
        ibmOpen = np.random.randn(1000)
        self.ibm = {'close': ibmClose, 'open': ibmOpen}
        self.dataSet = {'aapl': self.aapl, 'ibm': self.ibm}

    def testSecurityXAverageValueHolder(self):
        window = 10
        xav = SecurityXAverageValueHolder(window, ['close'], ['aapl', 'ibm'])
        exp_weight = 2.0 / (1.0 + window)

        expected = {}
        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            xav.push(data)

            value = xav.value
            for name in value.index:
                if i == 0:
                    expected[name] = self.dataSet[name]['close'][i]
                else:
                    expected[name] += exp_weight * (self.dataSet[name]['close'][i] - expected[name])
                calculated = value[name]
                self.assertAlmostEqual(expected[name], calculated, 12, 'at index {0}\n'
                                                                       'expected:   {1:.12f}\n'
                                                                       'calculated: {2:.12f}'
                                       .format(i, expected[name], calculated))

    def testSecurityMACDValueHolder(self):
        short = 5
        long = 10
        macd = SecurityMACDValueHolder(short, long, ['close'], ['aapl', 'ibm'])
        short_average = SecurityXAverageValueHolder(short, ['close'], ['aapl', 'ibm'])
        long_average = SecurityXAverageValueHolder(long, ['close'], ['aapl', 'ibm'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            macd.push(data)
            short_average.push(data)
            long_average.push(data)

            value = macd.value
            for name in value.index:
                expected = short_average.value[name] - long_average.value[name]
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculat: {2:.12f}'
                                       .format(i, expected, calculated))
