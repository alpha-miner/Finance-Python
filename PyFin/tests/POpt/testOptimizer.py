# -*- coding: utf-8 -*-
u"""
Created on 2016-4-18

@author: cheng.li
"""

import os
import unittest
import numpy as np
import pandas as pd
from PyFin.POpt.Optimizer import portfolio_returns
from PyFin.POpt.Optimizer import OptTarget
from PyFin.POpt.Optimizer import portfolio_optimization


class TestOptimizer(unittest.TestCase):
    def setUp(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/funds_data.csv')
        self.navData = pd.read_csv(filePath, index_col=0)
        self.instruments = sorted(['XT125045.XT',
                                   'XT130295.XT',
                                   'XT090981.XT',
                                   'XT113779.XT',
                                   'XT091121.XT',
                                   'XT121986.XT',
                                   'XT1205941.XT',
                                   'XT101310.XT',
                                   'XT113932.XT',
                                   'XT090776.XT',
                                   'XT112098.XT',
                                   'XT110161.XT',
                                   'XT113453.XT',
                                   'XT125853.XT'])

    def return_cal(self, navs):
        return np.log(navs[1:] / navs[:-1])

    def create_value_dict(self, names, values):
        return {name: value for name, value in zip(names, values)}

    def testPortfolioReturnsWithUnitWeight(self):
        weights = [0.0] * len(self.navData.columns)

        for i, col in enumerate(self.navData.columns):
            tmpWeights = weights[:]
            tmpWeights[i] = 1.0
            pReturns = portfolio_returns(tmpWeights, self.navData, rebalance=False)
            pReturns_ben = self.return_cal(navs=self.navData[col].values)
            self.assertTrue(np.allclose(pReturns, pReturns_ben))

    def testPortfolioReturnsWithRandomWeights(self):
        weights = np.random.uniform(0, 1.0, len(self.navData.columns))
        weights = weights / weights.sum()

        pReturns = portfolio_returns(weights, self.navData, rebalance=False)
        portNavs = np.dot(self.navData.values, weights)
        pReturns_ben = self.return_cal(navs=portNavs)
        self.assertTrue(np.allclose(pReturns, pReturns_ben))

    def testPortfolioReturnsWithRandomWeightsWithRebalance(self):
        weights = np.random.uniform(0, 1.0, len(self.navData.columns))
        weights = weights / weights.sum()

        pReturns = portfolio_returns(weights, self.navData, rebalance=True)
        returnsTable = self.return_cal(self.navData.values)
        pReturns_ben = np.dot(returnsTable, weights)
        self.assertTrue(np.allclose(pReturns, pReturns_ben))

    def testPortfolioOptimizerWithMaximumReturn(self):
        guess = [0.1 / len(self.instruments)] * len(self.instruments)
        out, fx, its, imode, smode = portfolio_optimization(guess, self.navData, OptTarget.RETURN, multiplier=50)
        matlab_res = self.create_value_dict(self.instruments, [4.75393550839560e-19,
                                                               0,
                                                               3.43546906184303e-19,
                                                               0,
                                                               0,
                                                               8.36677837797548e-20,
                                                               0,
                                                               5.76673494924112e-19,
                                                               4.05923081267658e-19,
                                                               0,
                                                               3.12250225675825e-17,
                                                               2.41998887084620e-20,
                                                               0,
                                                               1])
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

    def testPortfolioOptimizerWithMinimumVolatility(self):
        guess = [0.1 / len(self.instruments)] * len(self.instruments)
        out, fx, its, imode, smode = portfolio_optimization(guess, self.navData, OptTarget.VOL, multiplier=50)
        matlab_res = self.create_value_dict(self.instruments, [0,
                                                               0,
                                                               0,
                                                               6.99175721467524e-39,
                                                               1.87467007228981e-38,
                                                               0.00376413514611989,
                                                               0,
                                                               7.75214182640125e-38,
                                                               0.000712597692602067,
                                                               0,
                                                               0,
                                                               0.994237264821637,
                                                               0.00128600233964123,
                                                               7.05296610493373e-38])
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

    def testPortfolioOptimizerWithMaximumSharp(self):
        guess = [0.1 / len(self.instruments)] * len(self.instruments)
        out, fx, its, imode, smode = portfolio_optimization(guess, self.navData, OptTarget.SHARP, multiplier=50)
        matlab_res = self.create_value_dict(self.instruments, [3.72414607721023e-39,
                                                               5.58329252509498e-40,
                                                               8.50903300813402e-40,
                                                               9.42738796971393e-40,
                                                               4.83561316181437e-40,
                                                               0.00102720032914267,
                                                               4.40810381558358e-39,
                                                               0.000145735792353755,
                                                               0.000756493258973369,
                                                               3.91725820023446e-40,
                                                               0,
                                                               0.996553125979859,
                                                               0.00117153574239032,
                                                               0.000345908897280735])
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

    def testPortfolioOptimizerWithMaximumReturnWithRebalance(self):
        guess = [0.1 / len(self.instruments)] * len(self.instruments)
        out, fx, its, imode, smode = portfolio_optimization(guess, self.navData, OptTarget.RETURN, multiplier=50, rebalance=True)
        matlab_res = self.create_value_dict(self.instruments, [1.59234884538490e-17,
                                                               1.64287856671892e-18,
                                                               2.31111593326468e-33,
                                                               5.02151358940695e-17,
                                                               0,
                                                               9.41672950270667e-18,
                                                               1.64287856671892e-18,
                                                               2.82144347121750e-17,
                                                               0,
                                                               2.24595602784406e-17,
                                                               2.44504165203472e-16,
                                                               -1.68518870133883e-34,
                                                               0,
                                                               1.00000000000000])
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

    def testPortfolioOptimizerWithMinimumVolatilityWithRebalance(self):
        guess = [0.1 / len(self.instruments)] * len(self.instruments)
        out, fx, its, imode, smode = portfolio_optimization(guess, self.navData, OptTarget.VOL, multiplier=50, rebalance=True)
        matlab_res = self.create_value_dict(self.instruments, [1.17549435082229e-38,
                                                               0,
                                                               0,
                                                               1.68242628961440e-37,
                                                               0,
                                                               0.00209693665998001,
                                                               0,
                                                               1.53548949576161e-37,
                                                               0.00135190283349081,
                                                               0,
                                                               6.31828213566980e-38,
                                                               0.994988759101536,
                                                               0.00156240140499358,
                                                               0])
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

    def testPortfolioOptimizerWithMaximumSharpWithRebalance(self):
        guess = [0.1 / len(self.instruments)] * len(self.instruments)
        out, fx, its, imode, smode = portfolio_optimization(guess, self.navData, OptTarget.SHARP, multiplier=50, rebalance=True)
        matlab_res = self.create_value_dict(self.instruments, [2.76471048953164e-22,
                                                               7.19170303955622e-21,
                                                               2.52983701805491e-21,
                                                               1.94636169061746e-22,
                                                               0,
                                                               0,
                                                               0,
                                                               0.000165267959303058,
                                                               0.00137258304784842,
                                                               0,
                                                               2.06247008802505e-22,
                                                               0.995739327032537,
                                                               0.00134638898667400,
                                                               0.00137643297363735])
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)
