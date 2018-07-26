# -*- coding: utf-8 -*-
u"""
Created on 2017-1-25

@author: cheng.li
"""

import unittest
import copy
import pickle
import tempfile
import os
import numpy as np
import pandas as pd
from PyFin.Analysis.SeriesValues import SeriesValues


class TestSecurityValues(unittest.TestCase):

    def testSecurityValuesInit(self):
        data = np.array([1, 2, 3])
        index = ['c', 'b', 'a']

        test = SeriesValues(data, dict(zip(index, range(len(index)))))
        expected = dict(zip(index, data))

        for name in test.index():
            self.assertEqual(test[name], expected[name])

    def testSecurityValuesRank(self):

        data = np.array([3, 2, np.nan, np.nan, 4, 5])
        index = [1, 2, 3, 4, 5, 6]

        data = SeriesValues(data, index)
        test = data.rank()

        expected = SeriesValues(np.array([2, 1, np.nan, np.nan, 3, 4]), dict(zip(index, range(len(index)))))
        for name in test.index():
            if np.isnan(test[name]):
                self.assertTrue(np.isnan(expected[name]))
            else:
                self.assertEqual(test[name], expected[name])

    def testSecurityValuesRankWithGroup(self):
        data = np.random.randn(3000)
        groups = np.random.randint(0, 30, 3000)
        index = list(range(3000))

        data = SeriesValues(data, index)
        groups = SeriesValues(groups, index)

        test = data.rank(groups)

        pd_series = pd.Series(data.values)
        expected = pd_series.groupby(groups.values).rank()
        np.testing.assert_array_almost_equal(test.values, expected.values)

    def testSecurityValuesUnit(self):
        data = np.array([3, -2, np.nan, np.nan, 4, 5])
        index = [1, 2, 3, 4, 5, 6]
        test = SeriesValues(data, index)
        test = test.unit()

        expected = SeriesValues(data / np.nansum(np.abs(data)), dict(zip(index, range(len(index)))))
        for name in test.index():
            if np.isnan(test[name]):
                self.assertTrue(np.isnan(expected[name]))
            else:
                self.assertEqual(test[name], expected[name])

    def testSecurityValuesDeepCopy(self):
        data = np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test = SeriesValues(data, index)
        copied = copy.deepcopy(test)

        np.testing.assert_array_equal(test.values, copied.values)
        self.assertEqual(test.name_mapping, copied.name_mapping)

    def testSecurityValuesAdd(self):

        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SeriesValues(data1, index)
        test2 = SeriesValues(data2, index)

        calculated = test1 + test2
        expected = SeriesValues(data1 + data2, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = test1 + 2.0
        expected = SeriesValues(data1 + 2.0, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = 2.0 + test2
        expected = SeriesValues(2.0 + data2, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

    def testSecurityValuesSub(self):

        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SeriesValues(data1, index)
        test2 = SeriesValues(data2, index)

        calculated = test1 - test2
        expected = SeriesValues(data1 - data2, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = test1 - 2.0
        expected = SeriesValues(data1 - 2.0, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = 2.0 - test2
        expected = SeriesValues(2.0 - data2, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

    def testSecurityValuesMul(self):

        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SeriesValues(data1, index)
        test2 = SeriesValues(data2, index)

        calculated = test1 * test2
        expected = SeriesValues(data1 * data2, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = test1 * 2.0
        expected = SeriesValues(data1 * 2.0, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = 2.0 * test2
        expected = SeriesValues(2.0 * data2, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

    def testSecurityValuesXor(self):
        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SeriesValues(data1, index)
        test2 = SeriesValues(data2, index)

        calculated = test1 ^ test2

        expected = SeriesValues(np.array([data1, data2]).T, index=index)
        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        for name in index:
            np.testing.assert_array_almost_equal(calculated[name], expected[name])

    def testSecurityValuesDiv(self):

        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SeriesValues(data1, index)
        test2 = SeriesValues(data2, index)

        calculated = test1 / test2
        expected = SeriesValues(data1 / data2, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = test1 / 2.0
        expected = SeriesValues(data1 / 2.0, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = 2.0 / test2
        expected = SeriesValues(2.0 / data2, index)

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

    def testSecurityValuesRes(self):
        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SeriesValues(data1, index)
        test2 = SeriesValues(data2, index)

        calculated = test1.res(test2)
        expected = SeriesValues(np.zeros(len(data1)), index)

        np.testing.assert_array_almost_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        data1 = np.random.randn(100)
        data2 = np.random.randn(100)
        index = list(range(1, 101))

        test1 = SeriesValues(data1, index)
        test2 = SeriesValues(data2, index)

        calculated = test1.res(test2)
        expected = SeriesValues(data1 - np.dot(data2, data1) / np.dot(data2, data2) * data2, index)

        np.testing.assert_array_almost_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

    def testSecurityValuesPickle(self):
        data = np.array([3, 2, np.nan, np.nan, 4, 5])
        index = [1, 2, 3, 4, 5, 6]

        test = SeriesValues(data, index)

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(test, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            np.testing.assert_array_equal(test.values, pickled.values)
            self.assertEqual(test.name_mapping, pickled.name_mapping)

        os.unlink(f.name)
