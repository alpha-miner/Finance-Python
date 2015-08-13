# -*- coding: utf-8 -*-
u"""
Created on 2015-8-12

@author: cheng.li
"""

import unittest
from finpy.Analysis.SecurityValueHolders import SecurityValueHolder
from finpy.Analysis.SecurityValueHolders import NamedValueHolder
from finpy.Analysis.SecurityValueHolders import SecuritiesValues
from finpy.Analysis.TechnicalAnalysis import SecurityMovingAverage
from finpy.Analysis.TechnicalAnalysis import SecurityMovingMax


class TestSecurityValueHolders(unittest.TestCase):

    def setUp(self):
        pass

    def testSecuritiesValues(self):
        benchmarkValues = {'AAPL': 1.0, 'IBM': 2.0, 'GOOG': 3.0}
        values = SecuritiesValues(benchmarkValues)

        self.assertEqual(len(benchmarkValues), len(values))

        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key], values[key], 12)

        negValues = - values
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key], -negValues[key], 12)

        benchmarkValues2 = {'AAPL': 3.0, 'IBM': 2.0, 'GOOG': 1.0}
        values2 = SecuritiesValues(benchmarkValues2)
        addedValue = values + values2
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key] + benchmarkValues2[key], addedValue[key], 12)

        subbedValues = values - values2
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key] - benchmarkValues2[key], subbedValues[key], 12)

        multiValues = values * values2
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key] * benchmarkValues2[key], multiValues[key], 12)

        divValues = values / values2
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key] / benchmarkValues2[key], divValues[key], 12)

        # check operated with scalar
        addedValue = values + 2.0
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key] + 2.0, addedValue[key], 12)

        subbedValue = values - 2.0
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key] - 2.0, subbedValue[key], 12)

        multiValues = values * 2.0
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key] * 2.0, multiValues[key], 12)

        divValues = values / 2.0
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key] / 2.0, divValues[key], 12)

        # check right associate operators
        addedValue = 2.0 + values
        for key in benchmarkValues:
            self.assertAlmostEqual(2.0 + benchmarkValues[key], addedValue[key], 12)

        subbedValue = 2.0 - values
        for key in benchmarkValues:
            self.assertAlmostEqual(2.0 - benchmarkValues[key], subbedValue[key], 12)

        multiValues = 2.0 * values
        for key in benchmarkValues:
            self.assertAlmostEqual(2.0 * benchmarkValues[key], multiValues[key], 12)

        divValues = 2.0 / values
        for key in benchmarkValues:
            self.assertAlmostEqual(2.0 / benchmarkValues[key], divValues[key], 12)

        benchmarkValues3 = {'AAPL': 3.0, 'IBM': 2.0}
        with self.assertRaises(AssertionError):
            values3 = SecuritiesValues(benchmarkValues3)
            _ = values + values3

    def testBasicFunctions(self):
        window = 10
        pNames = ['close']
        symbolList = ['AAPL', 'IBM']
        testValueHolder = SecurityMovingAverage(window, pNames, symbolList)
        dependency = {
            name: pNames[0] for name in symbolList
        }

        self.assertEqual(set(testValueHolder.symbolList), set(symbolList))
        self.assertEqual(testValueHolder.dependency, dependency)
        self.assertEqual(testValueHolder.valueSize, 1)
        self.assertEqual(testValueHolder.window, window)

        # test binary operated value holder
        window2 = 5
        pNames2 = ['open']
        test2 = SecurityMovingMax(window2, pNames2, symbolList)
        binaryValueHolder = testValueHolder + test2
        dependency2 = {
            name: pNames + pNames2 for name in symbolList
        }

        self.assertEqual(set(binaryValueHolder.symbolList), set(symbolList))
        self.assertEqual(binaryValueHolder.dependency, dependency2)
        self.assertEqual(binaryValueHolder.valueSize, 1)
        self.assertEqual(binaryValueHolder.window, max(window, window2))

        # test compounded operated value holder
        test3 = SecurityMovingMax(window2, testValueHolder)
        self.assertEqual(set(test3.symbolList), set(symbolList))
        self.assertEqual(test3.dependency, dependency)
        self.assertEqual(test3.valueSize, 1)
        self.assertEqual(test3.window, window + window2 - 1)

        # test compounded twice
        test4 = SecurityMovingMax(window2, test3)
        self.assertEqual(set(test4.symbolList), set(symbolList))
        self.assertEqual(test4.dependency, dependency)
        self.assertEqual(test4.valueSize, 1)
        self.assertEqual(test4.window, window + 2 * window2 - 2)

    def testNamedValueHolder(self):
        window = 10
        pNames = 'close'
        symbolList = ['AAPL', 'IBM', 'GOOG']
        test = SecurityMovingAverage(window, pNames, symbolList)

        # single named value holder
        test1 = test['IBM']
        self.assertTrue(isinstance(test1, NamedValueHolder))
        self.assertEqual(set(test1.symbolList), set(['IBM']))
        self.assertEqual(test1.dependency, {'IBM': pNames})
        self.assertEqual(test1.valueSize, 1)
        self.assertEqual(test1.window, window)

        # multi-valued named value holder
        test2 = test['IBM', 'GOOG']
        dependency = {
            name: pNames for name in ['IBM', 'GOOG']
        }
        self.assertTrue(isinstance(test2, SecurityValueHolder))
        self.assertEqual(set(test2.symbolList), set(['IBM', 'GOOG']))
        self.assertEqual(test2.dependency, dependency)
        self.assertEqual(test2.valueSize, 1)
        self.assertEqual(test2.window, window)

