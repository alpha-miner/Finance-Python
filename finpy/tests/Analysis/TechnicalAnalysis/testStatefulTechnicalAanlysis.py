# -*- coding: utf-8 -*-
u"""
Created on 2015-8-11

@author: cheng.li
"""

import unittest
import math
import numpy as np
import copy
from collections import deque
from finpy.Analysis.TechnicalAnalysis import SecurityMovingAverage
from finpy.Analysis.TechnicalAnalysis import SecurityMovingMax
from finpy.Analysis.TechnicalAnalysis import SecurityMovingMinimum
from finpy.Analysis.TechnicalAnalysis import SecurityMovingSum
from finpy.Analysis.TechnicalAnalysis import SecurityMovingCountedPositive
from finpy.Analysis.TechnicalAnalysis import SecurityMovingPositiveAverage
from finpy.Analysis.TechnicalAnalysis import SecurityMovingLogReturn
from finpy.Analysis.TechnicalAnalysis import SecurityMovingHistoricalWindow


class TestStatefulTechnicalAnalysis(unittest.TestCase):

    def setUp(self):
        # preparing market data
        aaplClose = np.random.randn(1000)
        aaplOpen = np.random.randn(1000)
        self.aapl = {'close': aaplClose, 'open': aaplOpen}

        ibmClose = np.random.randn(1000)
        ibmOpen = np.random.randn(1000)
        self.ibm = {'close': ibmClose, 'open': ibmOpen}
        self.dataSet = {'AAPL': self.aapl, 'IBM': self.ibm}

    def testSecurityMovingAverage(self):
        window = 10
        ma1 = SecurityMovingAverage(window, ['close'], ['AAPL', 'IBM'])

        for i in range(len(self.aapl['close'])):
            data = {'AAPL': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['IBM'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                expected = np.mean(self.dataSet[name]['close'][start:(i+1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(RuntimeError):
            _ = SecurityMovingAverage(window, ['close', 'open'], ['AAPL', 'IBM'])

    def testSecurityMovingMax(self):
        window = 10
        ma1 = SecurityMovingMax(window, ['close'], ['AAPL', 'IBM'])

        for i in range(len(self.aapl['close'])):
            data = {'AAPL': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['IBM'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i+1 - window

            value = ma1.value
            for name in value:
                expected = np.max(self.dataSet[name]['close'][start:(i+1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(RuntimeError):
            _ = SecurityMovingMax(window, ['close', 'open'], ['AAPL', 'IBM'])

    def testSecurityMovingMinimum(self):
        window = 10
        ma1 = SecurityMovingMinimum(window, ['close'], ['AAPL', 'IBM'])

        for i in range(len(self.aapl['close'])):
            data = {'AAPL': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['IBM'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                expected = np.min(self.dataSet[name]['close'][start:(i+1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(RuntimeError):
            _ = SecurityMovingMinimum(window, ['close', 'open'], ['AAPL', 'IBM'])

    def testSecurityMovingSum(self):
        window = 10
        ma1 = SecurityMovingSum(window, ['close'], ['AAPL', 'IBM'])

        for i in range(len(self.aapl['close'])):
            data = {'AAPL': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['IBM'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                expected = np.sum(self.dataSet[name]['close'][start:(i+1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingCountedPositive(self):
        window = 10
        ma1 = SecurityMovingCountedPositive(window, ['close'], ['AAPL', 'IBM'])

        for i in range(len(self.aapl['close'])):
            data = {'AAPL': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['IBM'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                expected = np.sum(self.dataSet[name]['close'][start:(i+1)] > 0.0)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(RuntimeError):
            _ = SecurityMovingCountedPositive(window, ['close', 'open'], ['AAPL', 'IBM'])

    def testSecurityMovingPositiveAverage(self):
        window = 10
        ma1 = SecurityMovingPositiveAverage(window, ['close'], ['AAPL', 'IBM'])

        for i in range(len(self.aapl['close'])):
            data = {'AAPL': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['IBM'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                sampled = list(filter(lambda x: x > 0, self.dataSet[name]['close'][start:(i+1)]))
                if len(sampled) > 0:
                    expected = np.mean(sampled)
                else:
                    expected = 0.0
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(RuntimeError):
            _ = SecurityMovingPositiveAverage(window, ['close', 'open'], ['AAPL', 'IBM'])

    def testSecurityMovingLogReturn(self):
        window = 10
        ma1 = SecurityMovingLogReturn(window, ['close'], ['AAPL', 'IBM'])
        self.newDataSet = copy.deepcopy(self.dataSet)
        self.newDataSet['AAPL']['close'] = np.exp(self.newDataSet['AAPL']['close'])
        self.newDataSet['AAPL']['open'] = np.exp(self.newDataSet['AAPL']['open'])
        self.newDataSet['IBM']['close'] = np.exp(self.newDataSet['IBM']['close'])
        self.newDataSet['IBM']['open'] = np.exp(self.newDataSet['IBM']['open'])

        for i in range(len(self.aapl['close'])):
            data = {'AAPL': {'close': self.newDataSet['AAPL']['close'][i], 'open': self.newDataSet['AAPL']['open'][i]}}
            data['IBM'] = {'close': self.newDataSet['IBM']['close'][i], 'open': self.newDataSet['IBM']['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i - window

            value = ma1.value
            for name in value:
                sampled = self.newDataSet[name]['close'][start:(i+1)]
                if i >= 10:
                    expected = math.log(sampled[-1]/sampled[0])
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                     'expected:   {1:.12f}\n'
                                                                     'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(RuntimeError):
            _ = SecurityMovingLogReturn(window, ['close', 'open'], ['AAPL', 'IBM'])

    def testSecurityMovingHistoricalWindow(self):
        window = 5
        mh = SecurityMovingHistoricalWindow(window, 'close', ['AAPL', 'IBM'])

        benchmark = {'AAPL': deque(maxlen=window),
                     'IBM': deque(maxlen=window)}
        for i in range(len(self.aapl['close'])):
            data = {'AAPL': {'close': self.aapl['close'][i]},
                    'IBM': {'close': self.ibm['close'][i]}}

            mh.push(data)
            for name in benchmark:
                benchmark[name].append(data[name]['close'])

            if i >= 1:
                # check by get item methon
                container = mh.value
                for k in range(min(i+1, window)):
                    calculated = mh[k]
                    for name in calculated:
                        self.assertAlmostEqual(calculated[name], benchmark[name][-1-k], "at index {0} positon {1} and symbol {2}\n"
                                                                                        "expected:   {3}\n"
                                                                                        "calculated: {4}".format(i, k, name,
                                                                                                                 benchmark[name][-1],
                                                                                                                 calculated[name]))
                # check by value method
                for k in range(min(i+1, window)):
                    for name in calculated:
                        self.assertAlmostEqual(container[name][k], benchmark[name][-1-k], "at index {0} positon {1} and symbol {2}\n"
                                                                                        "expected:   {3}\n"
                                                                                        "calculated: {4}".format(i, k, name,
                                                                                                                 benchmark[name][-1],
                                                                                                                 container[name][k]))


    def testValueHolderCompounding(self):
        window = 10
        ma1 = SecurityMovingAverage(window, 'close', ['AAPL'])
        compounded1 = SecurityMovingMax(2, ma1)
        compounded2 = SecurityMovingAverage(2, ma1)

        self.assertEqual(compounded1.window, window + 1)

        container = [np.nan, np.nan]
        for i in range(len(self.aapl['close'])):
            data = {'AAPL': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            ma1.push(data)
            compounded1.push(data)
            compounded2.push(data)

            container[i % 2] = ma1.value['AAPL']

            if i >= 1:
                self.assertAlmostEqual(max(container), compounded1.value['AAPL'], 12)
                self.assertAlmostEqual(np.mean((container)), compounded2.value['AAPL'], 12)


