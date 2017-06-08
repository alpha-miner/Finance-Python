# -*- coding: utf-8 -*-
u"""
Created on 2017-6-8

@author: cheng.li
"""

import unittest
from PyFin.DateUtilities.Date import Date
from PyFin.CashFlows.CashFlow import SimpleCashFlow


class TestCashFlow(unittest.TestCase):

    def testSimpleCashFlow(self):
        cash_flow = SimpleCashFlow(100., Date(2017, 3, 28))

        self.assertAlmostEqual(cash_flow.amount(), 100.)
        self.assertEqual(cash_flow.date(), Date(2017, 3, 28))

    def testSimpleCashFlowComparing(self):
        cf1 = SimpleCashFlow(100., Date(2017, 3, 28))
        cf2 = SimpleCashFlow(100., Date(2017, 4, 1))

        self.assertTrue(cf1 < cf2)
        self.assertFalse(cf1 > cf2)

        cf2 = SimpleCashFlow(100., Date(2017, 3, 1))
        self.assertTrue(cf1 > cf2)
        self.assertFalse(cf1 < cf2)

        cf2 = SimpleCashFlow(100., Date(2017, 3, 28))
        self.assertTrue(cf1 == cf2)

    def testSimpleCashFlowHasOccurred(self):

        cf_date = Date.todaysDate() - 1

        cf1 = SimpleCashFlow(100., cf_date)
        self.assertTrue(cf1.hasOccurred())

        ref_date = cf_date - 1
        self.assertFalse(cf1.hasOccurred(ref_date))

        ref_date = cf_date
        self.assertTrue(cf1.hasOccurred(ref_date))
        self.assertFalse(cf1.hasOccurred(ref_date, include_ref_date=True))


if __name__ == '__main__':
    unittest.main()