# -*- coding: utf-8 -*-
u"""
Created on 2017-1-25

@author: cheng.li
"""

import unittest
import numpy as np
from collections import OrderedDict
from PyFin.Analysis.SecurityValues import SecurityValues


class TestSecurityValues(unittest.TestCase):

    def testSecurityValuesInit(self):
        data = np.array([1, 2, 3])
        index = ['c', 'b', 'a']

        test = SecurityValues(data, OrderedDict(zip(index, range(len(index)))))
        expected = dict(zip(index, data))

        for name in test.index:
            self.assertEqual(test[name], expected[name])

    def testSecurityValuesRank(self):

        data = np.array([3, 2, np.nan, np.nan, 4, 5])
        index = [1, 2, 3, 4, 5, 6]

        data = SecurityValues(data, OrderedDict(zip(index, range(len(index)))))
        test = data.rank()

        expected = SecurityValues([2, 1, np.nan, np.nan, 3, 4], OrderedDict(zip(index, range(len(index)))))
        for name in test.index:
            if np.isnan(test[name]):
                self.assertTrue(np.isnan(expected[name]))
            else:
                self.assertEqual(test[name], expected[name])

