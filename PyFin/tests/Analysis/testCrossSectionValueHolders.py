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
from PyFin.Analysis.CrossSectionValueHolders import CSTopNSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSBottomNSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSTopNPercentileSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSBottomNPercentileSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSAverageSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSAverageAdjustedSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSZScoreSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSFillNASecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSPercentileSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSResidueSecurityValueHolder


class TestCrossSectionValueHolder(unittest.TestCase):

    def setUp(self):
        np.random.seed(0)
        sample1 = np.random.randn(1000, 6)
        sample2 = np.random.randn(1000, 6)

        self.datas = {'aapl': {'close': sample1[:, 0], 'open': sample1[:, 1]},
                      'ibm': {'close': sample2[:, 0], 'open': sample2[:, 1]},
                      'goog': {'close': sample1[:, 2], 'open': sample1[:, 3]},
                      'baba': {'close': sample2[:, 2], 'open': sample2[:, 3]},
                      'tela': {'close': sample1[:, 4], 'open': sample1[:, 5]},
                      'nflx': {'close': sample2[:, 4], 'open': sample2[:, 5]}
                      }

    def testCSRankedSecurityValueHolderWithSymbolName(self):
        benchmark = SecurityLatestValueHolder(x='close')
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
        benchmark = SecurityLatestValueHolder(x='close')
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

    def testCSTopNSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close')
        n = 2
        topnHolder = CSTopNSecurityValueHolder(benchmark, n)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['goog'][Factors.OPEN][i]},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['baba'][Factors.OPEN][i]}}
            benchmark.push(data)
            topnHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal((-benchmarkValues).rank().values <= n, topnHolder.value.values)

    def testCSBottomNSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close')
        n = 2
        topnHolder = CSBottomNSecurityValueHolder(benchmark, n)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['goog'][Factors.OPEN][i]},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['baba'][Factors.OPEN][i]}}
            benchmark.push(data)
            topnHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal(benchmarkValues.rank().values <= n, topnHolder.value.values)

    def testCSRankedSecurityValueHolderWithGroups(self):
        benchmark = SecurityLatestValueHolder(x='close')
        groups = SecurityLatestValueHolder(x='ind')
        rankHolder = CSRankedSecurityValueHolder(benchmark, groups)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i],
                             'ind': 1.},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i],
                            'ind': 1.},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['goog'][Factors.OPEN][i],
                             'ind': 2.},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['baba'][Factors.OPEN][i],
                             'ind': 2.}}
            benchmark.push(data)
            rankHolder.push(data)
            benchmarkValues = benchmark.value
            groups = {'aapl': 1., 'ibm': 1., 'goog': 2., 'baba': 2.}
            expected_rank = pd.Series(benchmarkValues.to_dict()).groupby(groups).rank().values
            np.testing.assert_array_almost_equal(expected_rank, rankHolder.value.values)

    def testCSAverageSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close')
        meanHolder = CSAverageSecurityValueHolder(benchmark)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            meanHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal(benchmarkValues.values.mean(), meanHolder.value.values)

    def testCSAverageSecurityValueHolderWithGroup(self):
        benchmark = SecurityLatestValueHolder(x='close')
        groups = SecurityLatestValueHolder(x='ind')
        meanHolder = CSAverageSecurityValueHolder(benchmark, groups)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i],
                             'ind': 1.},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i],
                            'ind': 1.},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['goog'][Factors.OPEN][i],
                             'ind': 2.},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['baba'][Factors.OPEN][i],
                             'ind': 2.}}
            benchmark.push(data)
            meanHolder.push(data)
            benchmarkValues = benchmark.value
            groups = {'aapl': 1., 'ibm': 1., 'goog': 2., 'baba': 2.}
            expected_mean = pd.Series(benchmarkValues.to_dict()).groupby(groups).mean()
            calculated_mean = meanHolder.value

            for name in calculated_mean.index():
                if name in ['aapl', 'ibm']:
                    self.assertAlmostEqual(calculated_mean[name], expected_mean[1])
                else:
                    self.assertAlmostEqual(calculated_mean[name], expected_mean[2])

    def testCSPercentileSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close')
        perHolder = CSPercentileSecurityValueHolder(benchmark)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['goog'][Factors.OPEN][i]},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['baba'][Factors.OPEN][i]}
                    }
            benchmark.push(data)
            perHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal(benchmarkValues.rank().values / len(data), perHolder.value.values)

    def testCSTopNPercentileSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close')
        n = 0.3
        perHolder = CSTopNPercentileSecurityValueHolder(benchmark, n)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['goog'][Factors.OPEN][i]},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['baba'][Factors.OPEN][i]}
                    }
            benchmark.push(data)
            perHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal(((-benchmarkValues).rank().values / len(data)) <= n,
                                                 perHolder.value.values)

    def testCSBottomNPercentileSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close')
        n = 0.3
        perHolder = CSBottomNPercentileSecurityValueHolder(benchmark, n)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['goog'][Factors.OPEN][i]},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['baba'][Factors.OPEN][i]}
                    }
            benchmark.push(data)
            perHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal((benchmarkValues.rank().values / len(data)) <= n,
                                                 perHolder.value.values)

    def testCSPercentileSecurityValueHolderWithGroups(self):
        benchmark = SecurityLatestValueHolder(x='close')
        groups = SecurityLatestValueHolder(x='ind')
        perHolder = CSPercentileSecurityValueHolder(benchmark, groups)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i],
                             'ind': 1.},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i],
                            'ind': 1.},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['goog'][Factors.OPEN][i],
                             'ind': 2.},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['baba'][Factors.OPEN][i],
                             'ind': 2.}}
            benchmark.push(data)
            perHolder.push(data)
            benchmarkValues = benchmark.value
            groups = {'aapl': 1., 'ibm': 1., 'goog': 2., 'baba': 2.}
            expected_rank = pd.Series(benchmarkValues.to_dict()).groupby(groups) \
                .transform(lambda x: x.rank().values / len(x))
            np.testing.assert_array_almost_equal(expected_rank, perHolder.value.values)

    def testCSAverageAdjustedSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close')
        meanAdjustedHolder = CSAverageAdjustedSecurityValueHolder(benchmark)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]},
                    }
            benchmark.push(data)
            meanAdjustedHolder.push(data)
            benchmarkValues = benchmark.value
            np.testing.assert_array_almost_equal((benchmarkValues - benchmarkValues.mean()).values, meanAdjustedHolder.value.values)

    def testCSAverageAdjustedSecurityValueHolderWithGroups(self):
        benchmark = SecurityLatestValueHolder(x='close')
        groups = SecurityLatestValueHolder(x='ind')
        meanAdjustedHolder = CSAverageAdjustedSecurityValueHolder(benchmark, groups)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i],
                             'ind': 1.},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i],
                            'ind': 1.},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['goog'][Factors.OPEN][i],
                             'ind': 2.},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['baba'][Factors.OPEN][i],
                             'ind': 2.}}
            benchmark.push(data)
            meanAdjustedHolder.push(data)
            benchmarkValues = benchmark.value
            groups = {'aapl': 1., 'ibm': 1., 'goog': 2., 'baba': 2.}
            expected_rank = pd.Series(benchmarkValues.to_dict()).groupby(groups) \
                .transform(lambda x: x - x.mean())
            np.testing.assert_array_almost_equal(expected_rank, meanAdjustedHolder.value.values)

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

    def testCSFillNASecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close')
        groups = SecurityLatestValueHolder(x='ind')
        meanAdjustedHolder = CSFillNASecurityValueHolder(benchmark, groups)

        def cal_func(x):
            x[np.isnan(x)] = np.nanmean(x)
            return x

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i],
                             'ind': 1.},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i],
                            'ind': 1.},
                    'tela': {Factors.CLOSE: np.nan,
                            Factors.OPEN: self.datas['tela'][Factors.OPEN][i],
                            'ind': 1.},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['goog'][Factors.OPEN][i],
                             'ind': 2.},
                    'baba': {Factors.CLOSE: np.nan,
                             Factors.OPEN: self.datas['baba'][Factors.OPEN][i],
                             'ind': 2.},
                    'nflx': {Factors.CLOSE: self.datas['nflx'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['nflx'][Factors.OPEN][i],
                             'ind': 2.}
                    }
            benchmark.push(data)
            meanAdjustedHolder.push(data)
            benchmarkValues = benchmark.value
            groups = {'aapl': 1., 'ibm': 1., 'tela': 1., 'goog': 2., 'baba': 2., 'nflx': 2.}
            expected_rank = pd.Series(benchmarkValues.to_dict()).groupby(groups) \
                .transform(cal_func)
            np.testing.assert_array_almost_equal(expected_rank, meanAdjustedHolder.value.values)

    def testCSZscoreSecurityValueHolderWithGroups(self):
        benchmark = SecurityLatestValueHolder(x='close')
        groups = SecurityLatestValueHolder(x='ind')
        meanAdjustedHolder = CSZScoreSecurityValueHolder(benchmark, groups)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i],
                             'ind': 1.},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i],
                            'ind': 1.},
                    'goog': {Factors.CLOSE: self.datas['goog'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['goog'][Factors.OPEN][i],
                             'ind': 2.},
                    'baba': {Factors.CLOSE: self.datas['baba'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['baba'][Factors.OPEN][i],
                             'ind': 2.}}
            benchmark.push(data)
            meanAdjustedHolder.push(data)
            benchmarkValues = benchmark.value
            groups = {'aapl': 1., 'ibm': 1., 'goog': 2., 'baba': 2.}
            expected_rank = pd.Series(benchmarkValues.to_dict()).groupby(groups) \
                .transform(lambda x: (x - x.mean()) / x.std(ddof=0))
            np.testing.assert_array_almost_equal(expected_rank, meanAdjustedHolder.value.values)

    def testCSZResidueSecurityValueHolder(self):
        y = SecurityLatestValueHolder(x='close')
        x = SecurityLatestValueHolder(x='open')

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
            x_values = np.concatenate([np.ones(shape=(len(x_values), 1)), x_values.reshape(-1, 1)], axis=1)

            beta = np.dot(np.linalg.inv(np.dot(x_values.T, x_values)), np.dot(x_values.T, y_values.reshape(-1, 1)))
            expected = y_values - np.dot(x_values, beta).flatten()
            np.testing.assert_array_almost_equal(calculated, expected)
