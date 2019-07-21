# -*- coding: utf-8 -*-
u"""
Created on 2015-8-11

@author: cheng.li
"""

import unittest
import math
import numpy as np
import copy
import pickle
import tempfile
import os
from collections import deque
from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingDecay
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingVariance
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingStandardDeviation
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingArgMax
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMin
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingArgMin
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingRank
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
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingCorrelation


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

    def template_test_deepcopy(self, class_type, **kwargs):
        ma = class_type(**kwargs)

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        copied = copy.deepcopy(ma)

        for name in ma.value.index():
            self.assertAlmostEqual(ma.value[name], copied.value[name])

        for v in np.random.rand(20):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)
            copied.push(data)

            for name in ma.value.index():
                self.assertAlmostEqual(ma.value[name], copied.value[name])

    def template_test_pickle(self, class_type, **kwargs):
        ma = class_type(**kwargs)

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ma, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            for name in ma.value.index():
                self.assertAlmostEqual(ma.value[name], pickled.value[name])
        os.unlink(f.name)

        for v in np.random.rand(20):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)
            pickled.push(data)

            for name in ma.value.index():
                self.assertAlmostEqual(ma.value[name], pickled.value[name])

    def testSecurityMovingAverage(self):
        window = 10
        ma1 = SecurityMovingAverage(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.mean(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingDecay(self):
        window = 10
        ma1 = SecurityMovingDecay(window, ['close'])

        def calculate_decay(con, k):
            s = k - len(con) + 1
            c = (k + s) * (k - s + 1) / 2.
            sum_value = 0.
            for w in range(s, k+1):
                i = w - s
                sum_value += w * con[i]
            return sum_value / c

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = calculate_decay(self.dataSet[name]['close'][start:(i + 1)], window)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingAverageWithErrorValues(self):
        window = 5
        to_average = SecurityLatestValueHolder('open') / SecurityLatestValueHolder('close')
        ma = SecurityMovingAverage(window, to_average)

        container = {'aapl': deque(maxlen=window), 'ibm': deque(maxlen=window)}

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=1.0 if self.aapl['close'][i] >= 1.0 else 0.0,
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))

            ma.push(data)

            for name in data:
                res = data[name]['open'] / data[name]['close'] if data[name]['close'] != 0. else np.nan
                if res != np.inf and res != -np.inf and not math.isnan(res):
                    container[name].append(res)

            value = ma.value

            for name in value.index():
                expected = np.mean(container[name])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingAverageDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingAverage, window=10, x=['x'])

    def testSecurityMovingAveragePickle(self):
        self.template_test_pickle(SecurityMovingAverage, window=10, x=['x'])

    def testSecurityMovingVariance(self):
        window = 10
        var = SecurityMovingVariance(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))

            var.push(data)

            if i <= 1:
                continue

            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = var.value
            for name in value.index():
                expected = np.var(self.dataSet[name]['close'][start:(i + 1)]) * (i + 1. - start) / (i - start)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingVarianceDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingVariance, window=10, x=['x'])

    def testSecurityMovingVariancePickle(self):
        self.template_test_pickle(SecurityMovingVariance, window=10, x=['x'])

    def testSecurityMovingStandardDeviation(self):
        window = 10
        std = SecurityMovingStandardDeviation(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))

            std.push(data)

            if i <= 1:
                continue

            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = std.value
            for name in value.index():
                expected = math.sqrt(
                    np.var(self.dataSet[name]['close'][start:(i + 1)]) * (i + 1. - start) / (i - start))
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected,
                                                                                               calculated))

    def testSecurityMovingStandardDeviationDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingStandardDeviation, window=10, x=['x'])

    def testSecurityMovingStandardDeviationPickle(self):
        self.template_test_pickle(SecurityMovingStandardDeviation, window=10, x=['x'])

    def testSecurityMovingMax(self):
        window = 10
        ma1 = SecurityMovingMax(window, 'close')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.max(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingArgMax(self):
        window = 10
        ma1 = SecurityMovingArgMax(window, 'close')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = i - start - np.argmax(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingMaxDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingMax, window=10, x=['x'])

    def testSecurityMovingMaxPickle(self):
        self.template_test_pickle(SecurityMovingMax, window=10, x=['x'])

    def testSecurityMovingMin(self):
        window = 10
        ma1 = SecurityMovingMin(window, 'close')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.min(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingArgMin(self):
        window = 10
        ma1 = SecurityMovingArgMin(window, 'close')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = i - start - np.argmin(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingMinimumDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingMin, window=10, x='x')

    def testSecurityMovingMinimumPickle(self):
        self.template_test_pickle(SecurityMovingMin, window=10, x='x')

    def testSecurityMovingRank(self):
        window = 10
        mq = SecurityMovingRank(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index():
                con = self.dataSet[name]['close'][start:(i + 1)]
                sorted_con = sorted(con)
                expected = sorted_con.index(self.dataSet[name]['close'][i])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingCorrelation(self):
        window = 120
        x = SecurityLatestValueHolder('close')
        y = SecurityLatestValueHolder('open')
        mc = SecurityMovingCorrelation(window, x, y)

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mc.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mc.value
            for name in value.index():
                xs = self.dataSet[name]['close'][start:(i + 1)]
                ys = self.dataSet[name]['open'][start:(i + 1)]
                expected = np.corrcoef(xs, ys)[0, 1]
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingCorrelationNested(self):
        window = 120
        x = SecurityLatestValueHolder('close')
        y = SecurityLatestValueHolder('open')
        z = x > y
        mc = SecurityMovingCorrelation(window, x, z)

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mc.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mc.value
            for i, name in enumerate(value.index()):
                if i >= window:
                    xs = self.dataSet[name]['close'][start:(i + 1)]
                    ys = self.dataSet[name]['open'][start:(i + 1)]
                    zs = np.where(xs > ys, 1., 0.)
                    expected = np.corrcoef(xs, zs)[0, 1]
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                     'expected:   {1:.12f}\n'
                                                                     'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingQuantile(self):
        window = 10
        mq = SecurityMovingQuantile(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index():
                con = self.dataSet[name]['close'][start:(i + 1)]
                sorted_con = sorted(con)
                expected = sorted_con.index(self.dataSet[name]['close'][i]) / (len(sorted_con) - 1.)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingQuantileDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingQuantile, window=10, x=['x'])

    def testSecurityMovingQuantilePickle(self):
        self.template_test_pickle(SecurityMovingQuantile, window=10, x=['x'])

    def testSecurityMovingAllTrue(self):
        window = 3

        self.aapl['close'] = self.aapl['close'] > 0.
        self.ibm['close'] = self.ibm['close'] > 0.

        mq = SecurityMovingAllTrue(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index():
                con = self.dataSet[name]['close'][start:(i + 1)]
                expected = np.all(con)
                calculated = value[name]
                self.assertEqual(expected, calculated, 'at index {0}\n'
                                                       'expected:   {1}\n'
                                                       'calculated: {2}'.format(i, expected, calculated))

    def testSecurityMovingAllTrueDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingAllTrue, window=10, x=SecurityLatestValueHolder('x') > 0.)

    def testSecurityMovingAllTruePickle(self):
        self.template_test_pickle(SecurityMovingAllTrue, window=10, x=SecurityLatestValueHolder('x') > 0.)

    def testSecurityMovingAnyTrue(self):
        window = 3

        self.aapl['close'] = self.aapl['close'] > 0.
        self.ibm['close'] = self.ibm['close'] > 0.

        mq = SecurityMovingAnyTrue(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index():
                con = self.dataSet[name]['close'][start:(i + 1)]
                expected = np.any(con)
                calculated = value[name]
                self.assertEqual(expected, calculated, 'at index {0}\n'
                                                       'expected:   {1}\n'
                                                       'calculated: {2}'.format(i, expected, calculated))

    def testSecurityMovingAnyTrueDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingAnyTrue, window=10, x=SecurityLatestValueHolder('x') > 0.)

    def testSecurityMovingAnyTruePickle(self):
        self.template_test_pickle(SecurityMovingAnyTrue, window=10, x=SecurityLatestValueHolder('x') > 0.)

    def testSecurityMovingSum(self):
        window = 10
        ma1 = SecurityMovingSum(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.sum(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingSumDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingSum, window=10, x='x')

    def testSecurityMovingSumPickle(self):
        self.template_test_pickle(SecurityMovingSum, window=10, x='x')

    def testSecurityMovingCountedPositive(self):
        window = 10
        ma1 = SecurityMovingCountedPositive(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.sum(self.dataSet[name]['close'][start:(i + 1)] > 0.0)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingCountedPositiveDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingCountedPositive, window=10, x='x')

    def testSecurityMovingCountedPositivePickle(self):
        self.template_test_pickle(SecurityMovingCountedPositive, window=10, x='x')

    def testSecurityMovingPositiveAverage(self):
        window = 10
        ma1 = SecurityMovingPositiveAverage(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                sampled = list(filter(lambda x: x > 0, self.dataSet[name]['close'][start:(i + 1)]))
                if len(sampled) > 0:
                    expected = np.mean(sampled)
                else:
                    expected = 0.0
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingPositiveAverageDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingPositiveAverage, window=10, x='x')

    def testSecurityMovingPositiveAveragePickle(self):
        self.template_test_pickle(SecurityMovingPositiveAverage, window=10, x='x')

    def testSecurityMovingRSI(self):
        window = 10
        rsi = SecurityMovingRSI(window, ['close'])
        pos_avg = SecurityMovingPositiveDifferenceAverage(window, ['close'])
        neg_avg = SecurityMovingNegativeDifferenceAverage(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            rsi.push(data)
            pos_avg.push(data)
            neg_avg.push(data)

            value = rsi.value
            if i > 0:
                for name in value.index():
                    expected = pos_avg.value[name] / (pos_avg.value[name] - neg_avg.value[name]) * 100
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                     'expected:   {1:.12f}\n'
                                                                     'calculated: {2:.12f}'.format(i,
                                                                                                   expected,
                                                                                                   calculated))

    def testSecurityMovingRSIDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingRSI, window=10, x='x')

    def testSecurityMovingRSIPickle(self):
        self.template_test_pickle(SecurityMovingRSI, window=10, x='x')

    def testSecurityMovingLogReturn(self):
        window = 10
        ma1 = SecurityMovingLogReturn(window, ['close'])
        self.newDataSet = copy.deepcopy(self.dataSet)
        self.newDataSet['aapl']['close'] = np.exp(self.newDataSet['aapl']['close'])
        self.newDataSet['aapl']['open'] = np.exp(self.newDataSet['aapl']['open'])
        self.newDataSet['ibm']['close'] = np.exp(self.newDataSet['ibm']['close'])
        self.newDataSet['ibm']['open'] = np.exp(self.newDataSet['ibm']['open'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.newDataSet['aapl']['close'][i],
                                  open=self.newDataSet['aapl']['open'][i]),
                        ibm=dict(close=self.newDataSet['ibm']['close'][i],
                                 open=self.newDataSet['ibm']['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i - window

            value = ma1.value
            for name in value.index():
                sampled = self.newDataSet[name]['close'][start:(i + 1)]
                if i >= 10:
                    expected = math.log(sampled[-1] / sampled[0])
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                     'expected:   {1:.12f}\n'
                                                                     'calculated: {2:.12f}'.format(i, expected,
                                                                                                   calculated))

    def testSecurityMovingLogReturnDeepcopy(self):
        ma = SecurityMovingLogReturn(10, ['x'])

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        copied = copy.deepcopy(ma)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)
            copied.push(data)
            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], copied.value[name])

    def testSecurityMovingLogReturnPickle(self):
        ma = SecurityMovingLogReturn(10, ['x'])

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ma, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
        os.unlink(f.name)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)
            pickled.push(data)

            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], pickled.value[name])

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
