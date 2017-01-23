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
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingQuantile
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAllTrue
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAnyTrue
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingSum
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingCountedPositive
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingPositiveAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingPositiveDifferenceAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingNegativeDifferenceAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingRSI
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
        ma1 = SecurityMovingAverage(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index:
                expected = np.mean(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingAverage(window, ['close', 'open'])

    def testSecurityMovingMax(self):
        window = 10
        ma1 = SecurityMovingMax(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index:
                expected = np.max(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingMax(window, ['close', 'open'])

    def testSecurityMovingMinimum(self):
        window = 10
        ma1 = SecurityMovingMinimum(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index:
                expected = np.min(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingMinimum(window, ['close', 'open'])

    def testSecurityMovingQuantile(self):
        window = 10
        mq = SecurityMovingQuantile(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index:
                con = self.dataSet[name]['close'][start:(i + 1)]
                sorted_con = sorted(con)
                expected = sorted_con.index(self.dataSet[name]['close'][i]) / (len(sorted_con) - 1.)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingAllTru(self):
        window = 3

        self.aapl['close'] = self.aapl['close'] > 0.
        self.ibm['close'] = self.ibm['close'] > 0.

        mq = SecurityMovingAllTrue(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index:
                con = self.dataSet[name]['close'][start:(i + 1)]
                expected = np.all(con)
                calculated = value[name]
                self.assertEqual(expected, calculated, 'at index {0}\n'
                                                       'expected:   {1}\n'
                                                       'calculated: {2}'.format(i, expected, calculated))

    def testSecurityMovingAnyTru(self):
        window = 3

        self.aapl['close'] = self.aapl['close'] > 0.
        self.ibm['close'] = self.ibm['close'] > 0.

        mq = SecurityMovingAnyTrue(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index:
                con = self.dataSet[name]['close'][start:(i + 1)]
                expected = np.any(con)
                calculated = value[name]
                self.assertEqual(expected, calculated, 'at index {0}\n'
                                                       'expected:   {1}\n'
                                                       'calculated: {2}'.format(i, expected, calculated))

    def testSecurityMovingSum(self):
        window = 10
        ma1 = SecurityMovingSum(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index:
                expected = np.sum(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingCountedPositive(self):
        window = 10
        ma1 = SecurityMovingCountedPositive(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index:
                expected = np.sum(self.dataSet[name]['close'][start:(i + 1)] > 0.0)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingCountedPositive(window, ['close', 'open'])

    def testSecurityMovingPositiveAverage(self):
        window = 10
        ma1 = SecurityMovingPositiveAverage(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index:
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
            _ = SecurityMovingPositiveAverage(window, ['close', 'open'])

    def testSecurityMovingRSI(self):
        window = 10
        rsi = SecurityMovingRSI(window, ['close'])
        pos_avg = SecurityMovingPositiveDifferenceAverage(window, ['close'])
        neg_avg = SecurityMovingNegativeDifferenceAverage(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            data['ibm'] = {'close': self.ibm['close'][i], 'open': self.ibm['open'][i]}
            rsi.push(data)
            pos_avg.push(data)
            neg_avg.push(data)

            value = rsi.value
            if i > 0:
                for name in value.index:
                    expected = pos_avg.value[name] / (pos_avg.value[name] - neg_avg.value[name]) * 100
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                         'expected:   {1:.12f}\n'
                                                                         'calculated: {2:.12f}'.format(i,
                                                                                                       expected,
                                                                                                       calculated))

    def testSecurityMovingLogReturn(self):
        window = 10
        ma1 = SecurityMovingLogReturn(window, ['close'])
        self.newDataSet = copy.deepcopy(self.dataSet)
        self.newDataSet['aapl']['close'] = np.exp(self.newDataSet['aapl']['close'])
        self.newDataSet['aapl']['open'] = np.exp(self.newDataSet['aapl']['open'])
        self.newDataSet['ibm']['close'] = np.exp(self.newDataSet['ibm']['close'])
        self.newDataSet['ibm']['open'] = np.exp(self.newDataSet['ibm']['open'])

        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.newDataSet['aapl']['close'][i], 'open': self.newDataSet['aapl']['open'][i]}}
            data['ibm'] = {'close': self.newDataSet['ibm']['close'][i], 'open': self.newDataSet['ibm']['open'][i]}
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i - window

            value = ma1.value
            for name in value.index:
                sampled = self.newDataSet[name]['close'][start:(i + 1)]
                if i >= 10:
                    expected = math.log(sampled[-1] / sampled[0])
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                     'expected:   {1:.12f}\n'
                                                                     'calculated: {2:.12f}'.format(i, expected,
                                                                                                   calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingLogReturn(window, ['close', 'open'])

    def testSecurityMovingHistoricalWindow(self):
        window = 5
        mh = SecurityMovingHistoricalWindow(window, 'close')

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
                    for name in calculated.index:
                        self.assertAlmostEqual(calculated[name], benchmark[name][-1 - k],
                                               "at index {0} positon {1} and symbol {2}\n"
                                               "expected:   {3}\n"
                                               "calculated: {4}".format(i, k, name,
                                                                        benchmark[name][-1],
                                                                        calculated[name]))
                # check by value method
                for k in range(min(i + 1, window)):
                    for name in calculated.index:
                        self.assertAlmostEqual(container[name][k], benchmark[name][-1 - k],
                                               "at index {0} positon {1} and symbol {2}\n"
                                               "expected:   {3}\n"
                                               "calculated: {4}".format(i, k, name,
                                                                        benchmark[name][-1],
                                                                        container[name][k]))

    def testValueHolderCompounding(self):
        window = 10
        ma1 = SecurityMovingAverage(window, 'close')
        compounded1 = SecurityMovingMax(2, ma1)
        compounded2 = SecurityMovingAverage(2, ma1)

        self.assertEqual(compounded1.window, window + 2)

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
