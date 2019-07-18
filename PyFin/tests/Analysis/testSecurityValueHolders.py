# -*- coding: utf-8 -*-
u"""
Created on 2015-8-12

@author: cheng.li
"""

import unittest
import copy
import pickle
import tempfile
import os
import numpy as np
import pandas as pd
from PyFin.Enums import Factors
from PyFin.Analysis.SeriesValues import SeriesValues
from PyFin.Analysis.SecurityValueHolders import FilteredSecurityValueHolder
from PyFin.Analysis.SecurityValueHolders import SecurityCurrentValueHolder
from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from PyFin.Analysis.SecurityValueHolders import SecurityIIFValueHolder
from PyFin.Analysis.SecurityValueHolders import SecurityShiftedValueHolder
from PyFin.Analysis.SecurityValueHolders import SecurityDeltaValueHolder
from PyFin.Analysis.SecurityValueHolders import SecurityConstArrayValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMin
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingSum


class TestSecurityValueHolders(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        sample1 = np.random.randn(1000, 2)
        sample2 = np.random.randn(1000, 2)

        self.datas = {'aapl': {'close': sample1[:, 0], 'open': sample1[:, 1]},
                      'ibm': {'close': sample2[:, 0], 'open': sample2[:, 1]}}

        def check_values(expected, calculated):
            for name in calculated.index():
                self.assertEqual(calculated[name], expected[name], "for the name {0}\n"
                                                                   "expected:   {1}\n"
                                                                   "calculated: {2}".format(name,
                                                                                            expected[name],
                                                                                            calculated[name]))

        self.checker = check_values

    def testSecurityValueHolderWithGetItemUseInt(self):

        shift = 2
        benchmark = SecurityShiftedValueHolder(shift, SecurityLatestValueHolder(x='close'))
        testValueHolder = SecurityLatestValueHolder(x='close')[shift]

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            testValueHolder.push(data)

            if i < shift:
                continue

            calculated = testValueHolder.value
            expected = benchmark.value

            self.assertEqual(calculated.name_mapping, expected.name_mapping)
            np.testing.assert_array_almost_equal(calculated.values, expected.values)

    def testSecurityWhereValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close')

        testValueHolder = SecurityIIFValueHolder(benchmark > 0, benchmark, -benchmark)
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            testValueHolder.push(data)

            calculated = testValueHolder.value

            self.assertTrue(np.all((calculated > 0.).values))

            for name in calculated.index():
                rawValue = data[name][Factors.CLOSE]
                if rawValue > 0.:
                    self.assertAlmostEqual(rawValue, calculated[name])
                else:
                    self.assertAlmostEqual(-rawValue, calculated[name])

    def testSecurityConstArrayValueHolder(self):
        constArray = SecurityConstArrayValueHolder({'a': 1.0, 'b': 2.0})

        testValue = constArray.value
        expectedValue = SeriesValues(np.array([1.0, 2.0]), index=['a', 'b'])

        for name in expectedValue.index():
            self.assertAlmostEqual(testValue[name], expectedValue[name])

        testValue = constArray.value_by_name('a')
        self.assertAlmostEqual(1.0, testValue)

        testValue = constArray.value_by_names(['b', 'a', 'c'])
        expectedValue = SeriesValues(np.array([2.0, 1.0, np.nan]), index=['b', 'a', 'c'])

        np.testing.assert_array_almost_equal(testValue.values, expectedValue.values)
        self.assertEqual(testValue.name_mapping, expectedValue.name_mapping)

    def testSecurityConstArrayValueHolderWorkWithOthers(self):
        dictValue = {'aapl': 1.0, 'ibm': 2.0}
        constArray = SecurityConstArrayValueHolder(dictValue)

        benchmark = SecurityLatestValueHolder(x='close')
        multiplied = benchmark * constArray

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            constArray.push(data)
            multiplied.push(data)

            testValue = benchmark.value
            expectedValue = multiplied.value

            for name in expectedValue.index():
                self.assertAlmostEqual(testValue[name] * dictValue[name], expectedValue[name])

    def testSecurityAndOperatorValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close') > 0
        benchmark2 = SecurityLatestValueHolder(x='open') > 0

        testValueHolder = benchmark & benchmark2

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            testValueHolder.push(data)
            calculated = testValueHolder.value

            for name in calculated.index():
                close_value = data[name][Factors.CLOSE]
                open_value = data[name][Factors.OPEN]

                if close_value > 0. and open_value > 0:
                    self.assertTrue(calculated[name])
                else:
                    self.assertFalse(calculated[name])

    def testSecurityOrOperatorValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close') > 0
        benchmark2 = SecurityLatestValueHolder(x='open') > 0

        testValueHolder = benchmark | benchmark2

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            testValueHolder.push(data)
            calculated = testValueHolder.value

            for name in calculated.index():
                close_value = data[name][Factors.CLOSE]
                open_value = data[name][Factors.OPEN]

                if close_value > 0. or open_value > 0:
                    self.assertTrue(calculated[name])
                else:
                    self.assertFalse(calculated[name])

    def testSecurityXorOperatorValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close') > 0
        benchmark2 = SecurityLatestValueHolder(x='open') > 0

        testValueHolder = benchmark ^ benchmark2

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            testValueHolder.push(data)
            calculated = testValueHolder.value

            for name in calculated.index():
                close_value = data[name][Factors.CLOSE]
                open_value = data[name][Factors.OPEN]

                self.assertEqual(calculated[name][0], close_value > 0)
                self.assertEqual(calculated[name][1], open_value > 0)

    def testSecurityWhereValueHolderWithSymbolName(self):
        benchmark = SecurityLatestValueHolder(x='close')

        testValueHolder = SecurityIIFValueHolder(benchmark > 0, 'open', -benchmark)
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            testValueHolder.push(data)

            calculated = testValueHolder.value

            for name in calculated.index():
                rawValue = data[name][Factors.CLOSE]
                if rawValue > 0.:
                    self.assertAlmostEqual(data[name][Factors.OPEN], calculated[name])
                else:
                    self.assertAlmostEqual(-rawValue, calculated[name])

        testValueHolder = SecurityIIFValueHolder(benchmark > 0, 'open', 'close')
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            testValueHolder.push(data)

            calculated = testValueHolder.value

            for name in calculated.index():
                rawValue = data[name][Factors.CLOSE]
                if rawValue > 0.:
                    self.assertAlmostEqual(data[name][Factors.OPEN], calculated[name])
                else:
                    self.assertAlmostEqual(rawValue, calculated[name])

    def testSecurityWhereValueHolderWithMissingSymbol(self):
        benchmark = SecurityLatestValueHolder(x='open')
        benchmark2 = SecurityLatestValueHolder(x='close')
        testValueHolder = SecurityIIFValueHolder(benchmark < 0, 'open', -benchmark2)

        data = {'aapl': {'close': 2.0, 'open': 1.5},
                'ibm': {'open': 1.7}}

        benchmark.push(data)
        benchmark2.push(data)
        testValueHolder.push(data)

        calculated = testValueHolder.value

        self.assertAlmostEqual(calculated['aapl'], -data['aapl']['close'])
        self.assertTrue(np.isnan(calculated['ibm']))

    def testSecurityWhereValueHolderWithScalarValue(self):
        benchmark = SecurityLatestValueHolder(x='open')
        testValueHolder = SecurityIIFValueHolder(benchmark > 0, 1., -1.)
        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            testValueHolder.push(data)

            calculated = testValueHolder.value

            for name in calculated.index():
                rawValue = data[name][Factors.OPEN]
                if rawValue > 0.:
                    self.assertAlmostEqual(1., calculated[name])
                    self.assertAlmostEqual(1., testValueHolder.value_by_name(name))
                else:
                    self.assertAlmostEqual(-1., calculated[name])
                    self.assertAlmostEqual(-1., testValueHolder.value_by_name(name))

    def testFilteredSecurityValueHolder(self):
        benchmark = SecurityLatestValueHolder(x='close') > 0
        filtered = FilteredSecurityValueHolder(benchmark, benchmark)

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            filtered.push(data)
            try:
                _ = filtered['aapl']
                self.assertTrue(benchmark['aapl'])
            except KeyError:
                self.assertFalse(benchmark['aapl'])

            try:
                _ = filtered['ibm']
                self.assertTrue(benchmark['ibm'])
            except KeyError:
                self.assertFalse(benchmark['ibm'])

    def testFilteredSecurityValueHolderWithGetItemMethod(self):
        benchmark = SecurityLatestValueHolder(x='close') > 0
        filtered = benchmark[benchmark]

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            benchmark.push(data)
            filtered.push(data)

            try:
                _ = filtered['aapl']
                self.assertTrue(benchmark['aapl'])
            except KeyError:
                self.assertFalse(benchmark['aapl'])

            try:
                _ = filtered['ibm']
                self.assertTrue(benchmark['ibm'])
            except KeyError:
                self.assertFalse(benchmark['ibm'])

    def testFilteredSecurityValueHolderTransform(self):
        rawHolder = SecurityLatestValueHolder(x='close')
        fliterFlag = rawHolder >= 0
        filteredHolder = rawHolder[fliterFlag]

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            rawHolder.push(data)
            filteredHolder.push(data)

            filteredValues = filteredHolder.value >= 0.

            self.assertTrue(np.all(filteredValues.values))

            rawValues = rawHolder.value
            filteredValues = filteredHolder.value
            for name in rawValues.index():
                if rawValues[name] >= 0.:
                    self.assertTrue(name in filteredValues)

    def testSecurityValueHolderIsFull(self):
        test = SecurityMovingMax(2, x='close')

        data = {'aapl': {'close': 1.0},
                'ibm': {'close': 2.0}}
        test.push(data)
        self.assertEqual(test.isFull, False)

        data = {'aapl': {'close': 1.0},
                'ibm': {'close': 13.0}}
        test.push(data)
        self.assertEqual(test.isFull, True)

    def testSecuritiesValuesComparison(self):

        benchmarkValues = SeriesValues({'AAPL': 1.0, 'IBM': 2.0, 'GOOG': 3.0})
        calculated = benchmarkValues > 1.5
        expected = SeriesValues({'AAPL': False, 'IBM': True, 'GOOG': True})
        self.checker(expected, calculated)

        calculated = benchmarkValues < 1.5
        expected = SeriesValues({'AAPL': True, 'IBM': False, 'GOOG': False})
        self.checker(expected, calculated)

        calculated = benchmarkValues >= 1.0
        expected = SeriesValues({'AAPL': True, 'IBM': True, 'GOOG': True})
        self.checker(expected, calculated)

        calculated = benchmarkValues <= 2.0
        expected = SeriesValues({'AAPL': True, 'IBM': True, 'GOOG': False})
        self.checker(expected, calculated)

        benchmarkValues = SeriesValues({'AAPL': False, 'IBM': True, 'GOOG': False})
        calculated = benchmarkValues & True
        expected = SeriesValues({'AAPL': False, 'IBM': True, 'GOOG': False})
        self.checker(expected, calculated)

        calculated = True & benchmarkValues
        expected = SeriesValues({'AAPL': False, 'IBM': True, 'GOOG': False})
        self.checker(expected, calculated)

        calculated = benchmarkValues | True
        expected = SeriesValues({'AAPL': True, 'IBM': True, 'GOOG': True})
        self.checker(expected, calculated)

        calculated = True | benchmarkValues
        expected = SeriesValues({'AAPL': True, 'IBM': True, 'GOOG': True})
        self.checker(expected, calculated)

        benchmarkValues = SeriesValues({'AAPL': 1.0, 'IBM': 2.0, 'GOOG': 3.0})
        calculated = benchmarkValues == 2.0
        expected = SeriesValues({'AAPL': False, 'IBM': True, 'GOOG': False})
        self.checker(expected, calculated)

        calculated = benchmarkValues != 2.0
        expected = SeriesValues({'AAPL': True, 'IBM': False, 'GOOG': True})
        self.checker(expected, calculated)

    def testSecuritiesValuesArithmetic(self):
        benchmarkValues = {'AAPL': 1.0, 'IBM': 2.0, 'GOOG': 3.0}
        values = SeriesValues(benchmarkValues)

        self.assertEqual(len(benchmarkValues), len(values))

        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key], values[key], 12)

        negValues = -values
        for key in benchmarkValues:
            self.assertAlmostEqual(benchmarkValues[key], -negValues[key], 12)

        benchmarkValues2 = {'AAPL': 3.0, 'IBM': 2.0, 'GOOG': 1.0}
        values2 = SeriesValues(benchmarkValues2)
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
        pNames = 'close'
        symbolList = ['aapl', 'ibm']
        testValueHolder = SecurityMovingAverage(window, pNames)

        testValueHolder.push({'aapl': {'close': 1.0}, 'ibm': {'close': 2.0}})

        self.assertEqual(set(testValueHolder.symbolList), set(symbolList))
        self.assertEqual(testValueHolder.window, window)

        # test binary operated value holder
        window2 = 5
        pNames2 = 'open'
        test2 = SecurityMovingMax(window2, pNames2)
        binaryValueHolder = testValueHolder + test2

        self.assertEqual(binaryValueHolder.window, max(window, window2))

        # test compounded operated value holder
        test3 = SecurityMovingMax(window2, testValueHolder)
        self.assertEqual(test3.window, window + window2)

        # test compounded twice
        test4 = SecurityMovingMax(window2, test3)
        self.assertEqual(test4.window, window + 2 * window2)

    def testItemizedValueHolder(self):
        window = 10
        pNames = 'close'
        test = SecurityMovingAverage(window, pNames)
        test.push({'aapl': {'close': 10.0}, 'ibm': {'close': 15.0}, 'goog': {'close': 17.0}})
        test.push({'aapl': {'close': 12.0}, 'ibm': {'close': 10.0}, 'goog': {'close': 13.0}})

        expected = {'ibm': 12.5, 'goog': 15.0}
        for s in expected:
            self.assertAlmostEqual(test[s], expected[s])

    def testAddedSecurityValueHolders(self):
        window1 = 10
        window2 = 5
        dependency1 = Factors.CLOSE
        dependency2 = Factors.OPEN
        ma = SecurityMovingAverage(window1, dependency1)
        mm = SecurityMovingSum(window2, dependency2)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testAddedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = 'close'
        mm = SecurityMovingSum(window, dependency)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testAddedSecurityValueHolderWithName(self):
        window = 10
        dependency = 'close'
        mm = SecurityMovingSum(window, dependency)
        combined = 'open' + mm

        for i in range(len(self.datas['aapl']['close'])):
            data = {'aapl': {Factors.CLOSE: self.datas['aapl'][Factors.CLOSE][i],
                             Factors.OPEN: self.datas['aapl'][Factors.OPEN][i]},
                    'ibm': {Factors.CLOSE: self.datas['ibm'][Factors.CLOSE][i],
                            Factors.OPEN: self.datas['ibm'][Factors.OPEN][i]}}
            mm.push(data)
            combined.push(data)

            base = mm.value
            calculated = combined.value
            for name in calculated.index():
                self.assertAlmostEqual(base[name] + data[name]['open'], calculated[name], 12)

    def testRAddedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = 'close'
        ma = SecurityMovingAverage(window, dependency)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testSubbedSecurityValueHolder(self):
        window1 = 10
        window2 = 5
        dependency1 = Factors.CLOSE
        dependency2 = Factors.OPEN
        ma = SecurityMovingAverage(window1, dependency1)
        mm = SecurityMovingSum(window2, dependency2)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testSubbedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = 'close'
        mm = SecurityMovingSum(window, dependency)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testRSubbedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = 'close'
        ma = SecurityMovingAverage(window, dependency)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testMultipliedSecurityValueHolders(self):
        window1 = 10
        window2 = 5
        dependency1 = Factors.CLOSE
        dependency2 = Factors.OPEN
        ma = SecurityMovingAverage(window1, dependency1)
        mm = SecurityMovingSum(window2, dependency2)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testMultipliedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = 'close'
        mm = SecurityMovingSum(window, dependency)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testRMultipliedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = 'close'
        ma = SecurityMovingAverage(window, dependency)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testDividedSecurityValueHolders(self):
        window1 = 10
        window2 = 5
        dependency1 = Factors.CLOSE
        dependency2 = Factors.OPEN
        ma = SecurityMovingAverage(window1, dependency1)
        mm = SecurityMovingSum(window2, dependency2)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testDividedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = 'close'
        mm = SecurityMovingSum(window, dependency)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testRDividedSecurityValueHoldersWithScalar(self):
        window = 10
        dependency = 'close'
        ma = SecurityMovingAverage(window, dependency)
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
            for name in expected.index():
                self.assertAlmostEqual(expected[name], calculated[name], 12)

    def testCombinedSecurityValueHolderWithoutData(self):
        ma = SecurityMovingAverage(10, 'close')
        calculated = ma.value

        for name in calculated.index():
            self.assertTrue(np.isnan(calculated[name]))

    def testShiftedSecurityValueHolder(self):
        mm = SecurityMovingAverage(2, 'close')
        shifted1 = mm.shift(1)

        data1 = {'aapl': {'close': 1.0},
                 'ibm': {'close': 2.0},
                 'goog': {'close': 3.0}}
        shifted1.push(data1)
        calculated = shifted1.value
        for name in calculated.index():
            self.assertTrue(np.isnan(calculated[name]))

        data2 = {'aapl': {'close': 2.0},
                 'ibm': {'close': 3.0},
                 'goog': {'close': 4.0}}

        shifted1.push(data2)
        expected = SeriesValues({'aapl': 1.0,
                                 'ibm': 2.0,
                                 'goog': 3.0})
        calculated = shifted1.value
        for name in expected.index():
            self.assertAlmostEqual(expected[name], calculated[name])

        data3 = ({'aapl': {'close': 3.0},
                  'ibm': {'close': 4.0},
                  'goog': {'close': 5.0}})

        shifted1.push(data3)
        expected = SeriesValues({'aapl': 1.5,
                                 'ibm': 2.5,
                                 'goog': 3.5})
        calculated = shifted1.value
        for name in expected.index():
            self.assertAlmostEqual(expected[name], calculated[name])

    def testDeltaSecurityValueHolder(self):
        mm = SecurityMovingAverage(2, 'close')
        delta1 = SecurityDeltaValueHolder(2, mm)

        data1 = {'aapl': {'close': 1.0},
                 'ibm': {'close': 2.0},
                 'goog': {'close': 3.0}}
        delta1.push(data1)
        calculated = delta1.value
        for name in calculated.index():
            self.assertTrue(np.isnan(calculated[name]))

        data2 = {'aapl': {'close': 2.0},
                 'ibm': {'close': 3.0},
                 'goog': {'close': 4.0}}

        delta1.push(data2)

        data3 = {'aapl': {'close': 3.0},
                 'ibm': {'close': 4.0},
                 'goog': {'close': 5.0}}

        delta1.push(data3)

        expected = SeriesValues({'aapl': 1.5,
                                 'ibm': 1.5,
                                 'goog': 1.5})
        calculated = delta1.value
        for name in expected.index():
            self.assertAlmostEqual(expected[name], calculated[name])

        data4 = ({'aapl': {'close': 4.0},
                  'ibm': {'close': 5.0},
                  'goog': {'close': 6.0}})

        delta1.push(data4)
        expected = SeriesValues({'aapl': 2.0,
                                 'ibm': 2.0,
                                 'goog': 2.0})
        calculated = delta1.value
        for name in expected.index():
            self.assertAlmostEqual(expected[name], calculated[name])

    def testShiftedSecurityValueHolderWithLengthZero(self):
        mm = SecurityMovingAverage(2, 'close')
        with self.assertRaises(ValueError):
            _ = mm.shift(0)

    def testShiftedSecurityValueHolderDeepcopy(self):
        tested = SecurityShiftedValueHolder(2, SecurityLatestValueHolder('close'))

        data = dict(aapl=dict(close=1.0),
                    ibm=dict(close=2.0))
        tested.push(data)

        data = dict(aapl=dict(close=3.0),
                    ibm=dict(close=4.0))
        tested.push(data)

        data = dict(aapl=dict(close=5.0),
                    ibm=dict(close=6.0))
        tested.push(data)

        copied = copy.deepcopy(tested)

        expected = tested.value
        calcualted = copied.value
        for name in expected.index():
            self.assertAlmostEqual(expected[name], calcualted[name])

    def testShiftedSecurityValueHolderPickle(self):
        tested = SecurityShiftedValueHolder(2, SecurityLatestValueHolder('close'))

        data = dict(aapl=dict(close=1.0),
                    ibm=dict(close=2.0))
        tested.push(data)

        data = dict(aapl=dict(close=3.0),
                    ibm=dict(close=4.0))
        tested.push(data)

        data = dict(aapl=dict(close=5.0),
                    ibm=dict(close=6.0))
        tested.push(data)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(tested, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)

        expected = tested.value
        calcualted = pickled.value
        for name in expected.index():
            self.assertAlmostEqual(expected[name], calcualted[name])

    def testLtSecurityValueHolder(self):
        filter = SecurityLatestValueHolder('close') < 10.0
        ma = FilteredSecurityValueHolder(SecurityMovingAverage(10, 'close'), filter)

        data = {'aapl': {'close': 15.},
                'ibm': {'close': 8.},
                'goog': {'close': 7.}}

        ma.push(data)
        expected = {'ibm': 8.0, 'goog': 7.0}
        calculated = ma.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name], 15)

        data = {'aapl': {'close': 9.},
                'ibm': {'close': 11.},
                'goog': {'close': 8.}}

        ma.push(data)
        expected = {'aapl': 12.0, 'goog': 7.5}
        calculated = ma.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name], 15)

    def testFilterSecurityValueHolderWorkWithStr(self):
        filter = SecurityLatestValueHolder('code') == 2
        ma = FilteredSecurityValueHolder(SecurityMovingAverage(10, 'close'), filter)

        data = {'aapl': {'code': 1, 'close': 15.},
                'ibm': {'code': 2, 'close': 10.},
                'goog': {'code': 3, 'close': 7.}}

        ma.push(data)
        expected = {'ibm': 10.0}
        calculated = ma.value

        for name in calculated.index():
            self.assertAlmostEqual(expected[name], calculated[name], 15)

    def testLeSecurityValueHolder(self):
        filter = SecurityLatestValueHolder('close') <= 10.0
        ma = FilteredSecurityValueHolder(SecurityMovingAverage(10, 'close'), filter)

        data = {'aapl': {'close': 15.},
                'ibm': {'close': 10.},
                'goog': {'close': 7.}}

        ma.push(data)
        expected = {'ibm': 10.0, 'goog': 7.0}
        calculated = ma.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name], 15)

        data = {'aapl': {'close': 10.},
                'ibm': {'close': 11.},
                'goog': {'close': 8.}}

        ma.push(data)
        expected = {'aapl': 12.5, 'goog': 7.5}
        calculated = ma.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name], 15)

    def testGtSecurityValueHolder(self):
        filter = SecurityLatestValueHolder('close') > 10.0
        ma = FilteredSecurityValueHolder(SecurityMovingAverage(10, 'close'), filter)

        data = {'aapl': {'close': 15.},
                'ibm': {'close': 8.},
                'goog': {'close': 7.}}

        ma.push(data)
        expected = {'aapl': 15.}
        calculated = ma.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name], 15)

        data = {'aapl': {'close': 9.},
                'ibm': {'close': 11.},
                'goog': {'close': 8.}}

        ma.push(data)
        expected = {'ibm': 9.5}
        calculated = ma.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name], 15)

    def testGeSecurityValueHolder(self):
        filter = SecurityMovingAverage(1, 'close') >= 10.0
        ma = FilteredSecurityValueHolder(SecurityMovingAverage(10, 'close'), filter)

        data = {'aapl': {'close': 15.},
                'ibm': {'close': 10.},
                'goog': {'close': 7.}}

        ma.push(data)
        expected = {'aapl': 15., 'ibm': 10.}
        calculated = ma.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name], 15)

        data = {'aapl': {'close': 10.},
                'ibm': {'close': 11.},
                'goog': {'close': 8.}}

        ma.push(data)
        expected = {'aapl': 12.5, 'ibm': 10.5}
        calculated = ma.value
        for name in expected:
            self.assertAlmostEqual(expected[name], calculated[name], 15)

    def testTransformWithCategory(self):
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 1, 2, 3],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2],
                               dtype=float)

        expression = SecurityMovingMax(20, 'b') + SecurityMovingMin(20, 'c')
        calculated = expression.transform(test_df, name='new_factor', category_field='code')
        expected = [13., 13., 13., 13., 11., 9, 9.]

        np.testing.assert_array_almost_equal(calculated['new_factor'], expected)

    def testTransformWithoutCategory(self):
        test_df = pd.DataFrame({'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 2, 3, 4, 5, 6, 7],
                               dtype=float)

        expression = SecurityMovingMax(20, 'b') + SecurityMovingMin(20, 'c')
        calculated = expression.transform(test_df, name='new_factor')
        expected = [13., 13., 13., 13., 12., 11., 10.]
        np.testing.assert_array_almost_equal(calculated['new_factor'], expected)

    def testTransformWithDifferentGroup(self):
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 5, 6, 7],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2],
                               dtype=float)

        expression = SecurityMovingAverage(2, 'b')
        calculated = expression.transform(test_df, name='new_factor', category_field='code')

        expected = [4., 5., 6., 7., 6., 5., 4.]
        np.testing.assert_array_almost_equal(calculated['new_factor'], expected)

    def testTransformWithoutCategoryAndDuplicatedIndex(self):
        sample_data = pd.DataFrame(
            data={'code': [1, 2, 1, 2, 1, 2],
                  'open': [2.0, 1.0, 1.5, 3.0, 2.4, 3.5],
                  'close': [1.7, 1.6, 0.9, 3.8, 1.6, 2.1]},
            index=[1, 1, 2, 2, 3, 3],
            dtype=float
        )

        expression = SecurityMovingAverage(2, 'close')
        calculated = expression.transform(sample_data, name='new_factor')

        expected = sample_data.rolling(window=2).mean()

        np.testing.assert_array_almost_equal(calculated['new_factor'].values[1:],
                                             expected['close'].values[1:])

    def testSecurityCurrentValueHolder(self):
        current = SecurityCurrentValueHolder('x')

        data1 = dict(aapl=dict(x=1),
                     ibm=dict(x=2))

        current.push(data1)
        calculated = current.value
        for name in data1.keys():
            self.assertAlmostEqual(data1[name]['x'], calculated[name])

        data2 = dict(aapl=dict(x=3),
                     ibm=dict(x=np.nan))
        current.push(data2)
        calculated = current.value
        for name in data1.keys():
            expected = data2[name]['x']
            if not np.isnan(expected):
                self.assertAlmostEqual(expected, calculated[name])
            else:
                self.assertTrue(np.isnan(calculated[name]))

    def testSecurityLatestValueHolder(self):
        latest = SecurityLatestValueHolder('x')

        data1 = dict(aapl=dict(x=1),
                     ibm=dict(x=2))

        latest.push(data1)
        calculated = latest.value
        for name in data1.keys():
            self.assertAlmostEqual(data1[name]['x'], calculated[name])

        data2 = dict(aapl=dict(x=3),
                     ibm=dict(x=np.nan))
        latest.push(data2)
        calculated = latest.value
        for name in data1.keys():
            expected = data2[name]['x']
            if not np.isnan(expected):
                self.assertAlmostEqual(expected, calculated[name])
            else:
                self.assertAlmostEqual(data1[name]['x'], calculated[name])

    def testSecurityLatestValueHolderDeepcopy(self):
        latest = SecurityLatestValueHolder('x')

        data = dict(aapl=dict(x=1),
                    ibm=dict(x=2))

        latest.push(data)

        copied = copy.deepcopy(latest)

        calculated = copied.value

        for name in data.keys():
            self.assertAlmostEqual(data[name]['x'], calculated[name])

    def testSecurityLatestValueHolderPickle(self):
        latest = SecurityLatestValueHolder('x')

        data = dict(aapl=dict(x=1),
                    ibm=dict(x=2))

        latest.push(data)

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(latest, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            calculated = pickled.value

            for name in data.keys():
                self.assertAlmostEqual(data[name]['x'], calculated[name])

        os.unlink(f.name)

    def testSecurityLtOperatorValueHolderStr(self):
        holder = SecurityLatestValueHolder('x') < SecurityLatestValueHolder('y')
        self.assertEqual(str(holder), "''\\text{x}'' \\lt ''\\text{y}''")

    def testSecurityLeOperatorValueHolderStr(self):
        holder = SecurityLatestValueHolder('x') <= SecurityLatestValueHolder('y')
        self.assertEqual(str(holder), "''\\text{x}'' \\le ''\\text{y}''")

    def testSecurityGtOperatorValueHolderStr(self):
        holder = SecurityLatestValueHolder('x') > SecurityLatestValueHolder('y')
        self.assertEqual(str(holder), "''\\text{x}'' \\gt ''\\text{y}''")

    def testSecurityGeOperatorValueHolderStr(self):
        holder = SecurityLatestValueHolder('x') >= SecurityLatestValueHolder('y')
        self.assertEqual(str(holder), "''\\text{x}'' \\ge ''\\text{y}''")

    def testSecurityEqOperatorValueHolderStr(self):
        holder = SecurityLatestValueHolder('x') == SecurityLatestValueHolder('y')
        self.assertEqual(str(holder), "''\\text{x}'' == ''\\text{y}''")

    def testSecurityNeOperatorValueHolderStr(self):
        holder = SecurityLatestValueHolder('x') != SecurityLatestValueHolder('y')
        self.assertEqual(str(holder), "''\\text{x}'' \\neq ''\\text{y}''")

    def testSecurityAndOperatorValueHolderStr(self):
        holder = SecurityLatestValueHolder('x') & SecurityLatestValueHolder('y')
        self.assertEqual(str(holder), "''\\text{x}'' \& ''\\text{y}''")

    def testSecurityOrOperatorValueHolderStr(self):
        holder = SecurityLatestValueHolder('x') | SecurityLatestValueHolder('y')
        self.assertEqual(str(holder), "''\\text{x}'' | ''\\text{y}''")
