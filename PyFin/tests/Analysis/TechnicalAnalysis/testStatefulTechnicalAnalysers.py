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
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMinimum
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingSum
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingCountedPositive
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingPositiveAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingLogReturn
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingHistoricalWindow


class TestStatefulTechnicalAnalysis(unittest.TestCase):
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

    def testSecurityMovingAverage(self):
        window = 10
        ma1 = SecurityMovingAverage(window, ['close'], ['aapl', 'ibm'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                expected = np.mean(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingAverage(window, ['close', 'open'], ['aapl', 'ibm'])

    def testSecurityMovingMax(self):
        window = 10
        ma1 = SecurityMovingMax(window, ['close'], ['aapl', 'ibm'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                expected = np.max(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingMax(window, ['close', 'open'], ['aapl', 'ibm'])

    def testSecurityMovingMinimum(self):
        window = 10
        ma1 = SecurityMovingMinimum(window, ['close'], ['aapl', 'ibm'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                expected = np.min(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingMinimum(window, ['close', 'open'], ['aapl', 'ibm'])

    def testSecurityMovingSum(self):
        window = 10
        ma1 = SecurityMovingSum(window, ['close'], ['aapl', 'ibm'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                expected = np.sum(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingCountedPositive(self):
        window = 10
        ma1 = SecurityMovingCountedPositive(window, ['close'], ['aapl', 'ibm'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                expected = np.sum(self.dataSet[name]['close'][start:(i + 1)] > 0.0)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingCountedPositive(window, ['close', 'open'], ['aapl', 'ibm'])

    def testSecurityMovingPositiveAverage(self):
        window = 10
        ma1 = SecurityMovingPositiveAverage(window, ['close'], ['aapl', 'ibm'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value:
                sampled = list(filter(lambda x: x > 0, self.dataSet[name]['close'][start:(i + 1)]))
                if len(sampled) > 0:
                    expected = np.mean(sampled)
                else:
                    expected = 0.0
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingPositiveAverage(window, ['close', 'open'], ['aapl', 'ibm'])

    def testSecurityMovingLogReturn(self):
        window = 10
        ma1 = SecurityMovingLogReturn(window, ['close'], ['aapl', 'ibm'])
        self.newDataSet = copy.deepcopy(self.dataSet)
        self.newDataSet['aapl']['close'] = np.exp(self.newDataSet['aapl']['close'])
        self.newDataSet['aapl']['open'] = np.exp(self.newDataSet['aapl']['open'])
        self.newDataSet['ibm']['close'] = np.exp(self.newDataSet['ibm']['close'])
        self.newDataSet['ibm']['open'] = np.exp(self.newDataSet['ibm']['open'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.newDataSet['aapl']['close'][i], 'open': self.newDataSet['aapl']['open'][i]}}
            data['ibm'] = {'close': self.newDataSet['ibm']['close'][i], 'open': self.newDataSet['ibm']['open'][i]}
            ma1.push(data)
            if i < 10:
                start = 0
            else:
                start = i - window

            value = ma1.value
            for name in value:
                sampled = self.newDataSet[name]['close'][start:(i + 1)]
                if i >= 10:
                    expected = math.log(sampled[-1] / sampled[0])
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                     'expected:   {1:.12f}\n'
                                                                     'calculated: {2:.12f}'.format(i, expected,
                                                                                                   calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingLogReturn(window, ['close', 'open'], ['aapl', 'ibm'])

    def testSecurityMovingHistoricalWindow(self):
        window = 5
        mh = SecurityMovingHistoricalWindow(window, 'close', ['aapl', 'ibm'])

        benchmark = {'aapl': deque(maxlen=window),
                     'ibm': deque(maxlen=window)}
        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i]},
                    'ibm': {'close': self.ibm['close'][i]}}

            mh.push(data)
            for name in benchmark:
                benchmark[name].append(data[name]['close'])

            if i >= 1:
                # check by get item methon
                container = mh.value
                for k in range(min(i + 1, window)):
                    calculated = mh[k]
                    for name in calculated:
                        self.assertAlmostEqual(calculated[name], benchmark[name][-1 - k],
                                               "at index {0} positon {1} and symbol {2}\n"
                                               "expected:   {3}\n"
                                               "calculated: {4}".format(i, k, name,
                                                                        benchmark[name][-1],
                                                                        calculated[name]))
                # check by value method
                for k in range(min(i + 1, window)):
                    for name in calculated:
                        self.assertAlmostEqual(container[name][k], benchmark[name][-1 - k],
                                               "at index {0} positon {1} and symbol {2}\n"
                                               "expected:   {3}\n"
                                               "calculated: {4}".format(i, k, name,
                                                                        benchmark[name][-1],
                                                                        container[name][k]))

    def testValueHolderCompounding(self):
        window = 10
        ma1 = SecurityMovingAverage(window, 'close', ['aapl'])
        compounded1 = SecurityMovingMax(2, ma1)
        compounded2 = SecurityMovingAverage(2, ma1)

        self.assertEqual(compounded1.window, window + 1)

        container = [np.nan, np.nan]
        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            ma1.push(data)
            compounded1.push(data)
            compounded2.push(data)

            container[i % 2] = ma1.value['aapl']

            if i >= 1:
                self.assertAlmostEqual(max(container), compounded1.value['aapl'], 12)
                self.assertAlmostEqual(np.mean((container)), compounded2.value['aapl'], 12)
