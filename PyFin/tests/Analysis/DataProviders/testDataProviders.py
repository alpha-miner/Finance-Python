# -*- coding: utf-8 -*-
u"""
Created on 2015-8-19

@author: cheng.li
"""


import unittest
from PyFin.Analysis.DataProviders import DataProvider


class TestDataProviders(unittest.TestCase):

    def testDataProvider(self):
        dataSource = DataProvider()

        dataSource.set('aapl', 'close', 2.0)
        dataSource.set('ibm', 'open', 3.0)
        dataSource.set('goog', 'pe', 4.0)
        dataSource.set('aapl', 'rsi', 5.0)

        calculated = dataSource.data
        expected = {
            'aapl': {'close': 2.0, 'rsi': 5.0},
            'ibm': {'open': 3.0},
            'goog': {'pe': 4.0}
        }

        for name in expected:
            for field in expected[name]:
                eres = expected[name][field]
                cres = calculated[name][field]
                self.assertEqual(eres, cres, "for {0}'s field {1}\n"
                                             "expected:   {2}\n"
                                             "calculated: {3}".format(name, field, eres, cres))

        dataSource.clear()

        calculated = dataSource.data
        expected = {}
        self.assertEqual(calculated, expected, "cleared data provide\n"
                                               "expected:   {0}\n"
                                               "calculated: {1}".format(expected, calculated))

    def testDataProviderWithOverwrittern(self):
        dataSource = DataProvider()
        dataSource.set('aapl', 'close', 2.0)

        with self.assertRaises(ValueError):
            dataSource.set('aapl', 'close', 3.0)

