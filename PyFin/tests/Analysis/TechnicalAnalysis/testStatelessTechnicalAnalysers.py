# -*- coding: utf-8 -*-
u"""
Created on 2016-1-13

@author: cheng.li
"""

import unittest
import math
import numpy as np
import copy
import pickle
import tempfile
import os
from scipy.stats import norm
from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityDiffValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySignValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityXAverageValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityExpValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityLogValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityPowValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySqrtValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAbsValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityMACDValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityMaximumValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityMinimumValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityNormInvValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityCeilValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityFloorValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityRoundValueHolder


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

    def testSecuritySignValueHolder(self):
        sign = SecuritySignValueHolder('close')

        expected = {}
        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            sign.push(data)

            value = sign.value
            for name in value.index():
                expected[name] = np.sign(self.dataSet[name]['close'][i])
                calculated = value[name]
                self.assertAlmostEqual(expected[name], calculated, 12, 'at index {0}\n'
                                                                       'expected:   {1:.12f}\n'
                                                                       'calculated: {2:.12f}'
                                       .format(i, expected[name], calculated))

    def testSecurityXAverageValueHolder(self):
        window = 10
        xav = SecurityXAverageValueHolder(window, 'close')
        exp_weight = 2.0 / (1.0 + window)

        expected = {}
        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            xav.push(data)

            value = xav.value
            for name in value.index():
                if i == 0:
                    expected[name] = self.dataSet[name]['close'][i]
                else:
                    expected[name] += exp_weight * (self.dataSet[name]['close'][i] - expected[name])
                calculated = value[name]
                self.assertAlmostEqual(expected[name], calculated, 12, 'at index {0}\n'
                                                                       'expected:   {1:.12f}\n'
                                                                       'calculated: {2:.12f}'
                                       .format(i, expected[name], calculated))

    def testSecurityExpValueHolder(self):
        exp = SecurityExpValueHolder('close')

        expected = {}
        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            exp.push(data)

            value = exp.value
            for name in value.index():
                expected[name] = np.exp(self.dataSet[name]['close'][i])
                calculated = value[name]
                self.assertAlmostEqual(expected[name], calculated, 12, 'at index {0}\n'
                                                                       'expected:   {1:.12f}\n'
                                                                       'calculated: {2:.12f}'
                                       .format(i, expected[name], calculated))

    def testSecurityLogValueHolder(self):
        logExp = SecurityLogValueHolder(SecurityExpValueHolder('close'))

        expected = {}
        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            logExp.push(data)

            value = logExp.value
            for name in value.index():
                expected[name] = self.dataSet[name]['close'][i]
                calculated = value[name]
                self.assertAlmostEqual(expected[name], calculated, 12, 'at index {0}\n'
                                                                       'expected:   {1:.12f}\n'
                                                                       'calculated: {2:.12f}'
                                       .format(i, expected[name], calculated))

    def testSecurityPowValueHolder(self):
        n = 2
        pow = SecurityPowValueHolder('close', n)

        expected = {}
        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            pow.push(data)

            value = pow.value
            for name in value.index():
                expected[name] = math.pow(self.dataSet[name]['close'][i], n)
                calculated = value[name]
                self.assertAlmostEqual(expected[name], calculated, 12, 'at index {0}\n'
                                                                       'expected:   {1:.12f}\n'
                                                                       'calculated: {2:.12f}'
                                       .format(i, expected[name], calculated))

    def testSecuritySqrtValueHolder(self):
        n = 2
        sqrtPow = SecuritySqrtValueHolder(SecurityPowValueHolder('close', n))

        expected = {}
        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            sqrtPow.push(data)

            value = sqrtPow.value
            for name in value.index():
                expected[name] = math.sqrt(math.pow(self.dataSet[name]['close'][i], n))
                calculated = value[name]
                self.assertAlmostEqual(expected[name], calculated, 12, 'at index {0}\n'
                                                                       'expected:   {1:.12f}\n'
                                                                       'calculated: {2:.12f}'
                                       .format(i, expected[name], calculated))

    def testSecurityAbsValueHolder(self):
        absHolder = SecurityAbsValueHolder('close')

        expected = {}
        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            absHolder.push(data)

            value = absHolder.value
            for name in value.index():
                expected[name] = abs(self.dataSet[name]['close'][i])
                calculated = value[name]
                self.assertAlmostEqual(expected[name], calculated, 12, 'at index {0}\n'
                                                                       'expected:   {1:.12f}\n'
                                                                       'calculated: {2:.12f}'
                                       .format(i, expected[name], calculated))

    def testSecurityMACDValueHolder(self):
        short = 5
        long = 10
        macd = SecurityMACDValueHolder(short, long, 'close')
        short_average = SecurityXAverageValueHolder(short, 'close')
        long_average = SecurityXAverageValueHolder(long, 'close')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            macd.push(data)
            short_average.push(data)
            long_average.push(data)

            value = macd.value
            for name in value.index():
                expected = short_average.value[name] - long_average.value[name]
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculat: {2:.12f}'
                                       .format(i, expected, calculated))

    def testSecurityDiffValueHolder(self):

        mv = SecurityDiffValueHolder('close')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mv.push(data)

            if i > 0:
                value = mv.value
                for name in value.index():
                    expected = data[name]['close'] - previous_data[name]['close']
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                     'expected:   {1:.12f}\n'
                                                                     'calculat: {2:.12f}'
                                           .format(i, expected, calculated))
            previous_data = data

    def testSecurityDiffValueHolderDeepcopy(self):
        ma = SecurityDiffValueHolder('x')

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

        copied = copy.deepcopy(ma)
        for name in ma.value.index():
            self.assertAlmostEqual(ma.value[name], copied.value[name])

    def testSecurityDiffValueHolderPickle(self):
        ma = SecurityDiffValueHolder('x')

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(ma, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            for name in ma.value.index():
                self.assertAlmostEqual(ma.value[name], pickled.value[name])
        os.unlink(f.name)

        for v in np.random.rand(20):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(ma, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            for name in ma.value.index():
                self.assertAlmostEqual(ma.value[name], pickled.value[name])
        os.unlink(f.name)

    def testSecurityMaximumValueHolder(self):
        mm = SecurityMaximumValueHolder('open', 'close')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mm.push(data)

            value = mm.value
            for name in value.index():
                expected = max(getattr(self, name)['open'][i], getattr(self, name)['close'][i])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculat: {2:.12f}'
                                       .format(i, expected, calculated))

    def testSecurityMaximumValueHolderWithValueHolder(self):
        exp1 = SecurityLatestValueHolder('open')
        exp2 = SecurityLatestValueHolder('close')
        mm = SecurityMaximumValueHolder(exp1, exp2)

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mm.push(data)

            value = mm.value
            for name in value.index():
                expected = max(getattr(self, name)['open'][i], getattr(self, name)['close'][i])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculat: {2:.12f}'
                                       .format(i, expected, calculated))

    def testSecurityMinimumValueHolder(self):
        mm = SecurityMinimumValueHolder('open', 'close')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mm.push(data)

            value = mm.value
            for name in value.index():
                expected = min(getattr(self, name)['open'][i], getattr(self, name)['close'][i])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculat: {2:.12f}'
                                       .format(i, expected, calculated))

    def testSecurityMinimumValueHolderWithValueHolder(self):
        exp1 = SecurityLatestValueHolder('open')
        exp2 = SecurityLatestValueHolder('close')
        mm = SecurityMinimumValueHolder(exp1, exp2)

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mm.push(data)

            value = mm.value
            for name in value.index():
                expected = min(getattr(self, name)['open'][i], getattr(self, name)['close'][i])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculat: {2:.12f}'
                                       .format(i, expected, calculated))

    def testSecurityNormInvValueHolder(self):
        mm1 = SecurityNormInvValueHolder('open')
        mm2 = SecurityNormInvValueHolder('open', fullAcc=True)

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(open=norm.cdf(self.aapl['open'][i])),
                        ibm=dict(open=norm.cdf(self.ibm['open'][i])))
            mm1.push(data)
            mm2.push(data)

            value1 = mm1.value
            value2 = mm2.value
            for name in value1.index():
                expected = norm.ppf(data[name]['open'])
                calculated = value1[name]
                self.assertAlmostEqual(expected, calculated, 6, 'at index {0}\n'
                                                                'expected:   {1:.12f}\n'
                                                                'calculat: {2:.12f}'
                                       .format(i, expected, calculated))

                calculated = value2[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculat: {2:.12f}'
                                       .format(i, expected, calculated))

    def testSecurityCeilValueHolder(self):
        mm1 = SecurityCeilValueHolder('open')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(open=norm.cdf(self.aapl['open'][i])),
                        ibm=dict(open=norm.cdf(self.ibm['open'][i])))
            mm1.push(data)

            value1 = mm1.value
            for name in value1.index():
                expected = math.ceil(data[name]['open'])
                calculated = value1[name]
                self.assertAlmostEqual(expected, calculated, 6, 'at index {0}\n'
                                                                'expected:   {1:.12f}\n'
                                                                'calculat: {2:.12f}'
                                       .format(i, expected, calculated))

    def testSecurityFloorValueHolder(self):
        mm1 = SecurityFloorValueHolder('open')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(open=norm.cdf(self.aapl['open'][i])),
                        ibm=dict(open=norm.cdf(self.ibm['open'][i])))
            mm1.push(data)

            value1 = mm1.value
            for name in value1.index():
                expected = math.floor(data[name]['open'])
                calculated = value1[name]
                self.assertAlmostEqual(expected, calculated, 6, 'at index {0}\n'
                                                                'expected:   {1:.12f}\n'
                                                                'calculat: {2:.12f}'
                                       .format(i, expected, calculated))

    def testSecurityRoundValueHolder(self):
        mm1 = SecurityRoundValueHolder('open')

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(open=norm.cdf(self.aapl['open'][i])),
                        ibm=dict(open=norm.cdf(self.ibm['open'][i])))
            mm1.push(data)

            value1 = mm1.value
            for name in value1.index():
                expected = round(data[name]['open'])
                calculated = value1[name]
                self.assertAlmostEqual(expected, calculated, 6, 'at index {0}\n'
                                                                'expected:   {1:.12f}\n'
                                                                'calculat: {2:.12f}'
                                       .format(i, expected, calculated))
