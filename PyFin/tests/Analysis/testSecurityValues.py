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
from collections import OrderedDict
from PyFin.Analysis.SecurityValues import SecurityValues


class TestSecurityValues(unittest.TestCase):

    def testSecurityValuesInit(self):
        data = np.array([1, 2, 3])
        index = ['c', 'b', 'a']

        test = SecurityValues(data, OrderedDict(zip(index, range(len(index)))))
        expected = dict(zip(index, data))

        for name in test.index():
            self.assertEqual(test[name], expected[name])

    def testSecurityValuesRank(self):

        data = np.array([3, 2, np.nan, np.nan, 4, 5])
        index = [1, 2, 3, 4, 5, 6]

        data = SecurityValues(data, OrderedDict(zip(index, range(len(index)))))
        test = data.rank()

        expected = SecurityValues(np.array([2, 1, np.nan, np.nan, 3, 4]), OrderedDict(zip(index, range(len(index)))))
        for name in test.index():
            if np.isnan(test[name]):
                self.assertTrue(np.isnan(expected[name]))
            else:
                self.assertEqual(test[name], expected[name])

    def testSecurityValuesDeepCopy(self):
        data = np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test = SecurityValues(data, OrderedDict(zip(index, range(len(index)))))
        copied = copy.deepcopy(test)

        np.testing.assert_array_equal(test.values, copied.values)
        self.assertEqual(test.name_mapping, copied.name_mapping)

    def testSecurityValuesAdd(self):

        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SecurityValues(data1, OrderedDict(zip(index, range(len(index)))))
        test2 = SecurityValues(data2, OrderedDict(zip(index, range(len(index)))))

        calculated = test1 + test2
        expected = SecurityValues(data1 + data2, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = test1 + 2.0
        expected = SecurityValues(data1 + 2.0, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = 2.0 + test2
        expected = SecurityValues(2.0 + data2, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

    def testSecurityValuesSub(self):

        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SecurityValues(data1, OrderedDict(zip(index, range(len(index)))))
        test2 = SecurityValues(data2, OrderedDict(zip(index, range(len(index)))))

        calculated = test1 - test2
        expected = SecurityValues(data1 - data2, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = test1 - 2.0
        expected = SecurityValues(data1 - 2.0, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = 2.0 - test2
        expected = SecurityValues(2.0 - data2, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

    def testSecurityValuesMul(self):

        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SecurityValues(data1, OrderedDict(zip(index, range(len(index)))))
        test2 = SecurityValues(data2, OrderedDict(zip(index, range(len(index)))))

        calculated = test1 * test2
        expected = SecurityValues(data1 * data2, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = test1 * 2.0
        expected = SecurityValues(data1 * 2.0, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = 2.0 * test2
        expected = SecurityValues(2.0 * data2, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

    def testSecurityValuesDiv(self):

        data1 = np.array([3, 2, 2., 1., 4., 5.])
        data2 = -np.array([3, 2, 2., 1., 4., 5.])
        index = [1, 2, 3, 4, 5, 6]

        test1 = SecurityValues(data1, OrderedDict(zip(index, range(len(index)))))
        test2 = SecurityValues(data2, OrderedDict(zip(index, range(len(index)))))

        calculated = test1 / test2
        expected = SecurityValues(data1 / data2, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = test1 / 2.0
        expected = SecurityValues(data1 / 2.0, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

        calculated = 2.0 / test2
        expected = SecurityValues(2.0 / data2, OrderedDict(zip(index, range(len(index)))))

        np.testing.assert_array_equal(calculated.values, expected.values)
        self.assertEqual(calculated.name_mapping, expected.name_mapping)

    def testSecurityValuesPickle(self):
        data = np.array([3, 2, np.nan, np.nan, 4, 5])
        index = [1, 2, 3, 4, 5, 6]

        test = SecurityValues(data, OrderedDict(zip(index, range(len(index)))))

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(test, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            np.testing.assert_array_equal(test.values, pickled.values)
            self.assertEqual(test.name_mapping, pickled.name_mapping)

        os.unlink(f.name)
