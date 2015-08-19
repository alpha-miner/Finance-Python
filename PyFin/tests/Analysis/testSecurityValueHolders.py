# -*- coding: utf-8 -*-
u"""
Created on 2015-8-12

@author: cheng.li
"""

import unittest
from collections import deque
import numpy as np
from PyFin.Enums import Factors
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder
from PyFin.Analysis.SecurityValueHolders import SecuritiesValues
from PyFin.Analysis.SecurityValueHolders import dependencyCalculator
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingSum


class TestSecurityValueHolders(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        sample1 = np.random.randn(1000, 2)
        sample2 = np.random.randn(1000, 2)

        self.datas = {'aapl': {'close': sample1[:, 0], 'open': sample1[:, 1]},
                      'ibm': {'close': sample2[:, 0], 'open': sample2[:, 1]}}

        def check_values(expected, calculated):
            for name in calculated:
                self.assertEqual(calculated[name], expected[name], "for the name {0}\n"
                                                                   "expected:   {1}\n"
                                                                   "calculated: {2}".format(name,
                                                                                            expected[name],
                                                                                            calculated[name]))
        self.checker = check_values

    def testSecuritiesValuesIncompatibleSymbolList(self):
        values = SecuritiesValues({'AAPL': 3.0, 'IBM': 2.0, 'GOOG': 4.0})
        benchmarkValues3 = {'AAPL': 3.0, 'IBM': 2.0}
        with self.assertRaises(ValueError):
            values3 = SecuritiesValues(benchmarkValues3)
            _ = values + values3

    def testSecuritiesValuesComparison(self):

        benchmarkValues = SecuritiesValues({'AAPL': 1.0, 'IBM': 2.0, 'GOOG': 3.0})
        calculated = benchmarkValues > 1.5
        expected = SecuritiesValues({'AAPL': False, 'IBM': True, 'GOOG': True})
        self.checker(expected, calculated)

        calculated = benchmarkValues < 1.5
        expected = SecuritiesValues({'AAPL': True, 'IBM': False, 'GOOG': False})
        self.checker(expected, calculated)

        calculated = benchmarkValues >= 1.0
        expected = SecuritiesValues({'AAPL': True, 'IBM': True, 'GOOG': True})
        self.checker(expected, calculated)

        calculated = benchmarkValues <= 2.0
        expected = SecuritiesValues({'AAPL': True, 'IBM': True, 'GOOG': False})
        self.checker(expected, calculated)

        benchmarkValues = SecuritiesValues({'AAPL': False, 'IBM': True, 'GOOG': False})
        calculated = benchmarkValues & True
        expected = SecuritiesValues({'AAPL': False, 'IBM': True, 'GOOG': False})
        self.checker(expected, calculated)

        calculated = True & benchmarkValues
        expected = SecuritiesValues({'AAPL': False, 'IBM': True, 'GOOG': False})
        self.checker(expected, calculated)

        calculated = benchmarkValues | True
        expected = SecuritiesValues({'AAPL': True, 'IBM': True, 'GOOG': True})
        self.checker(expected, calculated)

        calculated = True | benchmarkValues
        expected = SecuritiesValues({'AAPL': True, 'IBM': True, 'GOOG': True})
        self.checker(expected, calculated)

        benchmarkValues = SecuritiesValues({'AAPL': 1.0, 'IBM': 2.0, 'GOOG': 3.0})
        calculated = benchmarkValues == 2.0
        expected = SecuritiesValues({'AAPL': False, 'IBM': True, 'GOOG': False})
        self.checker(expected, calculated)

        calculated = benchmarkValues != 2.0
        expected = SecuritiesValues({'AAPL': True, 'IBM': False, 'GOOG': True})
        self.checker(expected, calculated)

    def testSecuritiesValuesArithmetic(self):
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

    def testBasicFunctions(self):
        window = 10
        pNames = ['close']
        symbolList = ['aapl', 'ibm']
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
        for name in dependency2:
            self.assertEqual(set(binaryValueHolder.dependency[name]), set(dependency2[name]))
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

    def testDependencyCalculation(self):
        h1 = SecurityMovingMax(5, 'close', ['AAPL', 'IBM'])
        h2 = SecurityMovingAverage(6, 'open', ['GOOG'])
        h3 = SecurityMovingAverage(4, h1)
        h4 = SecurityMovingAverage(3, 'pe', ['AAPL', 'IBM', 'GOOG'])
        h5 = SecurityMovingAverage(3, Factors.PE, ['QQQ'])

        expected = {'close': ['aapl', 'ibm'],
                    'pe': ['goog', 'aapl', 'ibm', 'qqq'],
                    'open': ['goog']}
        calculated = dict(dependencyCalculator(h1, h2, h3, h4, h5))
        for name in expected:
            self.assertEqual(set(expected[name]), set(calculated[name]))

    def testItemizedValueHolder(self):
        window = 10
        pNames = 'close'
        symbolList = ['AAPL', 'IBM', 'GOOG']
        test = SecurityMovingAverage(window, pNames, symbolList)

        # single named value holder
        test1 = test['IBM']
        self.assertEqual(set(test1.symbolList), set(['ibm']))
        self.assertEqual(test1.dependency, {'ibm': pNames})
        self.assertEqual(test1.valueSize, 1)
        self.assertEqual(test1.window, window)

        # multi-valued named value holder
        test2 = test['IBM', 'GOOG']
        dependency = {
            name: pNames for name in ['ibm', 'goog']
            }
        self.assertTrue(isinstance(test2, SecurityValueHolder))
        self.assertEqual(set(test2.symbolList), set(['ibm', 'goog']))
        self.assertEqual(test2.dependency, dependency)
        self.assertEqual(test2.valueSize, 1)
        self.assertEqual(test2.window, window)

        # wrong type of item
        with self.assertRaises(TypeError):
            _ = test[1]

    def testAddedSecurityValueHolders(self):
        window1 = 10
        window2 = 5
        dependency1 = Factors.CLOSE
        dependency2 = Factors.OPEN
        ma = SecurityMovingAverage(window1, dependency1, ['aapl', 'ibm'])
        mm = SecurityMovingSum(window2, dependency2, ['aapl', 'ibm'])
        combined = ma + mm

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            ma.push(data)
            mm.push(data)
            combined.push(data)

            expected = ma.value + mm.value
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testAddedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = ['close']
        mm = SecurityMovingSum(window, dependency, ['aapl', 'ibm'])
        combined = 2.0 + mm
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            mm.push(data)
            combined.push(data)

            expected = 2.0 + mm.value
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testRAddedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = ['close']
        ma = SecurityMovingAverage(window, dependency, ['aapl', 'ibm'])
        combined = ma + 2.0
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            ma.push(data)
            combined.push(data)

            expected = ma.value + 2.0
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testSubbedSecurityValueHolder(self):
        window1 = 10
        window2 = 5
        dependency1 = Factors.CLOSE
        dependency2 = Factors.OPEN
        ma = SecurityMovingAverage(window1, dependency1, ['aapl', 'ibm'])
        mm = SecurityMovingSum(window2, dependency2, ['aapl', 'ibm'])
        combined = ma - mm

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            ma.push(data)
            mm.push(data)
            combined.push(data)

            expected = ma.value - mm.value
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testSubbedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = ['close']
        mm = SecurityMovingSum(window, dependency, ['aapl', 'ibm'])
        combined = 2.0 - mm
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            mm.push(data)
            combined.push(data)

            expected = 2.0 - mm.value
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testRSubbedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = ['close']
        ma = SecurityMovingAverage(window, dependency, ['aapl', 'ibm'])
        combined = ma - 2.0
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            ma.push(data)
            combined.push(data)

            expected = ma.value - 2.0
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testMultipliedSecurityValueHolders(self):
        window1 = 10
        window2 = 5
        dependency1 = Factors.CLOSE
        dependency2 = Factors.OPEN
        ma = SecurityMovingAverage(window1, dependency1, ['aapl', 'ibm'])
        mm = SecurityMovingSum(window2, dependency2, ['aapl', 'ibm'])
        combined = ma * mm

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            ma.push(data)
            mm.push(data)
            combined.push(data)

            expected = ma.value * mm.value
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testMultipliedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = ['close']
        mm = SecurityMovingSum(window, dependency, ['aapl', 'ibm'])
        combined = 2.0 * mm
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            mm.push(data)
            combined.push(data)

            expected = 2.0 * mm.value
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testRMultipliedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = ['close']
        ma = SecurityMovingAverage(window, dependency, ['aapl', 'ibm'])
        combined = ma * 2.0
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            ma.push(data)
            combined.push(data)

            expected = ma.value * 2.0
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testDividedSecurityValueHolders(self):
        window1 = 10
        window2 = 5
        dependency1 = Factors.CLOSE
        dependency2 = Factors.OPEN
        ma = SecurityMovingAverage(window1, dependency1, ['aapl', 'ibm'])
        mm = SecurityMovingSum(window2, dependency2, ['aapl', 'ibm'])
        combined = ma / mm

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            ma.push(data)
            mm.push(data)
            combined.push(data)

            expected = ma.value / mm.value
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testDividedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = ['close']
        mm = SecurityMovingSum(window, dependency, ['aapl', 'ibm'])
        combined = 2.0 / mm
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            mm.push(data)
            combined.push(data)

            expected = 2.0 / mm.value
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testRDividedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = ['close']
        ma = SecurityMovingAverage(window, dependency, ['aapl', 'ibm'])
        combined = ma / 2.0
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            ma.push(data)
            combined.push(data)

            expected = ma.value / 2.0
            calculated = combined.value
            for name in expected:
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testCombinedSecurityValueHolderWithoutData(self):
        ma = SecurityMovingAverage(10, 'close', ['aapl', 'ibm', 'goog'])
        expected = {'aapl': np.nan,
                    'ibm': np.nan,
                    'goog': np.nan}
        calculated = ma.value

        for name in expected:
            self.assertIs(expected[name], calculated[name])

    def testShiftedSecurityValueHolder(self):
        mm = SecurityMovingAverage(2, 'close', ['aapl', 'ibm', 'goog'])
        shifted1 = mm.shift(1)

        data1 = {'aapl': {'close': 1.0},
                 'ibm': {'close': 2.0},
                 'goog': {'close': 3.0}}
        shifted1.push(data1)
        expected = {'aapl': np.nan,
                    'ibm': np.nan,
                    'goog': np.nan}
        calculated = shifted1.value
        for name in expected:
            self.assertIs(expected[name], calculated[name])

        data2 = {'aapl': {'close': 2.0},
                 'ibm': {'close': 3.0},
                 'goog': {'close': 4.0}}
        shifted1.push(data2)
        expected = {'aapl': 1.0,
                   'ibm': 2.0,
                   'goog': 3.0}
        calculated = shifted1.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name])

        data3 = {'aapl': {'close': 3.0},
                 'ibm': {'close': 4.0},
                 'goog': {'close': 5.0}}
        shifted1.push(data3)
        expected = {'aapl': 1.5,
                    'ibm': 2.5,
                    'goog': 3.5}
        calculated = shifted1.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name])

    def testShiftedSecurityValueHolderWithLengthZero(self):
        mm = SecurityMovingAverage(2, 'close', ['aapl', 'ibm', 'goog'])
        with self.assertRaises(ValueError):
            _ = mm.shift(0)

    def testCompoundedSecurityValueHolder(self):
        ma = SecurityMovingAverage(2, 'close', ['aapl', 'ibm'])
        compounded = ma >> SecurityMovingMax(3)

        container = {'aapl': deque(maxlen=3), 'ibm': deque(maxlen=3)}
        expected = {'aapl': 0.0, 'ibm': 0.0}
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i]}}
            ma.push(data)
            maRes = ma.value
            for name in maRes:
                container[name].append(maRes[name])
                expected[name] = max(container[name])

            compounded.push(data)
            calculated = compounded.value
            for name in calculated:
                self.assertAlmostEqual(expected[name], calculated[name], 12, "for {0} at index {1}\n"
                                                                             "expected:   {2}\n"
                                                                             "calculated: {3}"
                                       .format(name, i, expected[name], calculated[name]))



