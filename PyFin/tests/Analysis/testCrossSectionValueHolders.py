# -*- coding: utf-8 -*-
u"""
Created on 2017-1-6

@author: cheng.li
"""

import unittest
import numpy as np
import pandas as pd
from PyFin.Enums import Factors
from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSRankedSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSAverageSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSAverageAdjustedSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSQuantileSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSZScoreSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSPercentileSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSResidueSecurityValueHolder


class TestCrossSectionValueHolder(unittest.TestCase):

    def setUp(self):
        np.random.seed(0)
        sample1 = np.random.randn(1000, 2)
        sample2 = np.random.randn(1000, 2)

        self.datas = {'aapl': {'close': sample1[:, 0], 'open': sample1[:, 1]},
                      'ibm': {'close': sample2[:, 0], 'open': sample2[:, 1]}}

    def testCSRankedSecurityValueHolderWithSymbolName(self):
        benchmark = SecurityLatestValueHolder(dependency='close')
        rankHolder = CSRankedSecurityValueHolder('close')

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            rankHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal(benchmarkValues.rank().values, rankHolder.value.values)

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
            np.testing.assert_array_almost_equal(benchmarkValues.rank().values, rankHolder.value.values)

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
            np.testing.assert_array_almost_equal(benchmarkValues.mean(), meanHolder.value.values)

    def testCSPercentileSecurityValueHolder(self):
        percent = 50
        benchmark = SecurityLatestValueHolder(dependency='close')
        perHolder = CSPercentileSecurityValueHolder(percent, benchmark)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            perHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal(np.percentile(benchmarkValues.values, 50), perHolder.value.values)

    def testCSAverageAdjustedSecurityValueHolder(self):
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
            np.testing.assert_array_almost_equal(benchmarkValues.values - benchmarkValues.mean(), meanAdjustedHolder.value.values)

    def testCSQuantileSecurityValueHolder(self):
        keys = list(range(1, 11))
        values = list(range(10, 0, -1))

        data = {}

        for i, k in enumerate(keys):
            data[k] = {}
            data[k]['close'] = values[i]

        quantile_value = CSQuantileSecurityValueHolder('close')
        quantile_value.push(data)

        calculated = quantile_value.value

        data = np.linspace(1., 0., 10)

        expected = pd.Series(data=data, index=[x for x in range(1, 11)])

        np.testing.assert_array_almost_equal(expected.values, calculated.values)

    def testCSZscoreSecurityValueHolder(self):
        keys = list(range(1, 11))
        values = list(range(10, 0, -1))

        data = {}

        for i, k in enumerate(keys):
            data[k] = {}
            data[k]['close'] = values[i]

        quantile_value = CSZScoreSecurityValueHolder('close')
        quantile_value.push(data)

        calculated = quantile_value.value

        data = np.linspace(10., 1., 10)
        expected = (data - data.mean()) / data.std()

        np.testing.assert_array_almost_equal(expected, calculated.values)

    def testCSZResidueSecurityValueHolder(self):
        y = SecurityLatestValueHolder(dependency='close')
        x = SecurityLatestValueHolder(dependency='open')

        res = CSResidueSecurityValueHolder(y, x)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            y.push(data)
            x.push(data)
            res.push(data)

            calculated = res.value.values
            y_values = y.value.values
            x_values = x.value.values

            beta = np.dot(y_values, x_values) / np.dot(x_values, x_values)
            expected = y_values - beta * x_values
            np.testing.assert_array_almost_equal(calculated, expected)



