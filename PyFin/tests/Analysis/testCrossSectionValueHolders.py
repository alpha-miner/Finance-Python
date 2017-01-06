# -*- coding: utf-8 -*-
u"""
Created on 2017-1-6

@author: cheng.li
"""

import unittest
import numpy as np
from PyFin.Enums import Factors
from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSRankedSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSAverageSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSAverageAdjustedSecurityValueHolder


class TestCrossSectionValueHolder(unittest.TestCase):

    def setUp(self):
        np.random.seed(0)
        sample1 = np.random.randn(1000, 2)
        sample2 = np.random.randn(1000, 2)

        self.datas = {'aapl': {'close': sample1[:, 0], 'open': sample1[:, 1]},
                      'ibm': {'close': sample2[:, 0], 'open': sample2[:, 1]}}

    def testCSRankedSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(dependency='close')
        rankHolder = CSRankedSecurityValueHolder(benchmark)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            rankHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal(benchmarkValues.rank(ascending=False), rankHolder.value)

    def testCSAverageSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(dependency='close')
        meanHolder = CSAverageSecurityValueHolder(benchmark)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            meanHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal(benchmarkValues.mean(), meanHolder.value)

    def testCSAverageSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(dependency='close')
        meanAdjustedHolder = CSAverageAdjustedSecurityValueHolder(benchmark)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            meanAdjustedHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal(benchmarkValues - benchmarkValues.mean(), meanAdjustedHolder.value)