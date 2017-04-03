# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

import unittest
import copy
import tempfile
import pickle
import os
from PyFin.DateUtilities import Period
from PyFin.Enums import TimeUnits


class TestPeriod(unittest.TestCase):
    def testBasicArithmic(self):
        # test bad normalize
        testPriod = Period(length=1, units=TimeUnits.Years)
        testPriod._units = 10
        with self.assertRaises(TypeError):
            testPriod.normalize()

        # test plus method
        p1 = Period(length=0, units=TimeUnits.Days)
        p2 = Period(length=10, units=TimeUnits.Months)
        calculated = p1 + p2
        self.assertEqual(p2, calculated, "added value {0} should be equal to {1}".format(calculated, p2))

        p1 = Period(length=2, units=TimeUnits.Years)
        p2 = Period(length=13, units=TimeUnits.Months)
        calculated = p1 + p2
        expected = Period(length=37, units=TimeUnits.Months)
        self.assertEqual(expected, calculated, "added value {0} should be equal to {1}".format(calculated, expected))

        p2 = Period(length=2, units=TimeUnits.Weeks)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.Days)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p1 = Period(length=13, units=TimeUnits.Months)
        p2 = Period(length=2, units=TimeUnits.Years)
        calculated = p1 + p2
        expected = Period(length=37, units=TimeUnits.Months)
        self.assertEqual(expected, calculated, "added value {0} should be equal to {1}".format(calculated, expected))

        p2 = Period(length=2, units=TimeUnits.Weeks)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.Days)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p1 = Period(length=2, units=TimeUnits.Weeks)
        p2 = Period(length=7, units=TimeUnits.Days)
        calculated = p1 + p2
        expected = Period(length=21, units=TimeUnits.Days)
        self.assertEqual(expected, calculated, "added value {0} should be equal to {1}".format(calculated, expected))

        p2 = Period(length=2, units=TimeUnits.Months)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.Years)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p1 = Period(length=7, units=TimeUnits.Days)
        p2 = Period(length=2, units=TimeUnits.Weeks)
        calculated = p1 + p2
        expected = Period(length=21, units=TimeUnits.Days)
        self.assertEqual(expected, calculated, "added value {0} should be equal to {1}".format(calculated, expected))

        p2 = Period(length=2, units=TimeUnits.Months)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.Years)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p1 = Period(length=7, units=TimeUnits.BDays)

        p2 = Period(length=2, units=TimeUnits.Months)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.Days)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.Weeks)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.Years)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(length=2, units=TimeUnits.BDays)
        self.assertEqual(p1 + p2, Period('9B'))

        # test negative operator
        p1 = Period(length=-13, units=TimeUnits.Weeks)
        p2 = -p1
        self.assertEqual(p2, Period(length=13, units=TimeUnits.Weeks))

        # test less operator
        p1 = Period(length=0, units=TimeUnits.Days)
        p2 = Period(length=-3, units=TimeUnits.BDays)
        self.assertTrue(p2 < p1)

        # test sub operator
        p1 = Period(length=0, units=TimeUnits.Days)
        p2 = Period(length=-3, units=TimeUnits.BDays)
        self.assertEqual(p1 - p2, Period('3b'))

        # test string representation
        p1 = Period(length=12, units=TimeUnits.Months)
        self.assertEqual("1Y", p1.__str__())

    def testComparingOperators(self):
        p1 = Period(length=0, units=TimeUnits.Days)
        p2 = Period(length=1, units=TimeUnits.Days)
        self.assertTrue(p1 < p2)

        p1 = Period(length=13, units=TimeUnits.Months)
        p2 = Period(length=1, units=TimeUnits.Years)
        self.assertTrue(not p1 < p2)

        p1 = Period(length=1, units=TimeUnits.Years)
        p2 = Period(length=13, units=TimeUnits.Months)
        self.assertTrue(p1 < p2)

        p1 = Period(length=13, units=TimeUnits.Days)
        p2 = Period(length=2, units=TimeUnits.Weeks)
        self.assertTrue(p1 < p2)

        p1 = Period(length=2, units=TimeUnits.Weeks)
        p2 = Period(length=13, units=TimeUnits.Days)
        self.assertTrue(not p1 < p2)

        p1 = Period(length=1, units=TimeUnits.Years)
        p2 = Period(length=56, units=TimeUnits.Weeks)
        self.assertTrue(p1 < p2)

        p1 = Period(length=56, units=TimeUnits.Weeks)
        p2 = Period(length=1, units=TimeUnits.Years)
        self.assertTrue(not p1 < p2)

        p1 = Period(length=21, units=TimeUnits.Weeks)
        p2 = Period(length=5, units=TimeUnits.Months)

        with self.assertRaises(ValueError):
            _ = p1 < p2

        p1 = Period(length=21, units=TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 < p2

        # test not equal operator
        p1 = Period(length=1, units=TimeUnits.Days)
        p2 = Period(length=1, units=TimeUnits.Days)
        self.assertTrue(not p1 != p2)

        p2 = Period(length=1, units=TimeUnits.Years)
        self.assertTrue(p1 != p2)

        # test greater than operator
        p1 = Period(length=1, units=TimeUnits.Days)
        p2 = Period(length=2, units=TimeUnits.Days)
        self.assertEqual(p1 < p2, not p1 > p2)

    def testYearsMonthsAlgebra(self):
        oneYear = Period(length=1, units=TimeUnits.Years)
        sixMonths = Period(length=6, units=TimeUnits.Months)
        threeMonths = Period(length=3, units=TimeUnits.Months)

        n = 4
        flag = oneYear / n == threeMonths
        self.assertTrue(flag, "division error: {0} / {1:d}"
                              " not equal to {2}".format(oneYear, n, threeMonths))

        n = 2
        flag = oneYear / n == sixMonths
        self.assertTrue(flag, "division error: {0} / {1:d}"
                              " not equal to {2}".format(oneYear, n, sixMonths))

        sum = threeMonths
        sum += sixMonths
        flag = sum == Period(length=9, units=TimeUnits.Months)
        self.assertTrue(flag, "sum error: {0}"
                              " + {1}"
                              " != {2}".format(threeMonths, sixMonths, Period(length=9, units=TimeUnits.Months)))

        sum += oneYear
        flag = sum == Period(length=21, units=TimeUnits.Months)
        self.assertTrue(flag, "sum error: {0}"
                              " + {1}"
                              " + {2}"
                              " != {3}".format(threeMonths, sixMonths, oneYear, Period(length=21, units=TimeUnits.Months)))

        twelveMonths = Period(length=12, units=TimeUnits.Months)
        flag = twelveMonths.length() == 12
        self.assertTrue(flag, "normalization error: TwelveMonths.length"
                              " is {0:d}"
                              " instead of 12".format(twelveMonths.length()))
        flag = twelveMonths.units() == TimeUnits.Months
        self.assertTrue(flag, "normalization error: TwelveMonths.units"
                              " is {0:d}"
                              " instead of {1:d}".format(twelveMonths.units(), TimeUnits.Months))

        normalizedTwelveMonths = Period(length=12, units=TimeUnits.Months)
        normalizedTwelveMonths = normalizedTwelveMonths.normalize()
        flag = normalizedTwelveMonths.length() == 1
        self.assertTrue(flag, "normalization error: TwelveMonths.length"
                              " is {0:d}"
                              " instead of 1".format(twelveMonths.length()))
        flag = normalizedTwelveMonths.units() == TimeUnits.Years
        self.assertTrue(flag, "normalization error: TwelveMonths.units"
                              " is {0:d}"
                              " instead of {1:d}".format(twelveMonths.units(), TimeUnits.Years))

        thirtyDays = Period(length=30, units=TimeUnits.Days)
        normalizedThirtyDays = thirtyDays.normalize()
        flag = normalizedThirtyDays.units() == TimeUnits.Days
        self.assertTrue(flag, "normalization error: ThirtyDays.units"
                              " is {0:d}"
                              " instead of {1:d}".format(normalizedThirtyDays.units(), TimeUnits.Days))

        thirtyBDays = Period(length=30, units=TimeUnits.BDays)
        normalizedThirtyBDays = thirtyBDays.normalize()
        flag = normalizedThirtyBDays.units() == TimeUnits.BDays
        self.assertTrue(flag, "normalization error: ThirtyBDays.units"
                              " is {0:d}"
                              " instead of {1:d}".format(normalizedThirtyBDays.units(), TimeUnits.BDays))

    def testWeeksDaysAlgebra(self):
        twoWeeks = Period(length=2, units=TimeUnits.Weeks)
        oneWeek = Period(length=1, units=TimeUnits.Weeks)
        threeDays = Period(length=3, units=TimeUnits.Days)
        oneDay = Period(length=1, units=TimeUnits.Days)

        n = 2
        flag = twoWeeks / n == oneWeek
        self.assertTrue(flag, "division error: {0} / {1:d}"
                              " not equal to {2}".format(twoWeeks, n, oneWeek))

        n = 7
        flag = oneWeek / 7 == oneDay
        self.assertTrue(flag, "division error: {0} / {1:d}"
                              " not equal to {2}".format(oneWeek, n, oneDay))

        sum = threeDays
        sum += oneDay
        flag = sum == Period(length=4, units=TimeUnits.Days)
        self.assertTrue(flag, "sum error: {0}"
                              " + {1}"
                              " != {2}".format(threeDays, oneDay, Period(length=4, units=TimeUnits.Days)))

        sum += oneWeek
        flag = sum == Period(length=11, units=TimeUnits.Days)
        self.assertTrue(flag, "sum error: {0}"
                              " + {1}"
                              " + {2}"
                              " != {3}".format(threeDays, oneDay, oneWeek, Period(length=11, units=TimeUnits.Days)))

        sevenDays = Period(length=7, units=TimeUnits.Days)
        flag = sevenDays.length() == 7
        self.assertTrue(flag, "normalization error: sevenDays.length"
                              " is {0:d}"
                              " instead of 7".format(sevenDays.length()))
        flag = sevenDays.units() == TimeUnits.Days
        self.assertTrue(flag, "normalization error: sevenDays.units"
                              " is {0:d}"
                              " instead of {1:d}".format(sevenDays.units(), TimeUnits.Days))

        normalizedSevenDays = sevenDays.normalize()
        flag = normalizedSevenDays.length() == 1
        self.assertTrue(flag, "normalization error: normalizedSevenDays.length"
                              " is {0:d}"
                              " instead of 1".format(normalizedSevenDays.length()))
        flag = normalizedSevenDays.units() == TimeUnits.Weeks
        self.assertTrue(flag, "normalization error: TwelveMonths.units"
                              " is {0:d}"
                              " instead of {1:d}".format(normalizedSevenDays.units(), TimeUnits.Weeks))

    def testPeriodDeepCopy(self):

        p1 = Period('36m')
        p2 = copy.deepcopy(p1)

        self.assertEqual(p1, p2)

    def testPeriodPickle(self):
        p1 = Period('36m')

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(p1, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled_period = pickle.load(f2)
            self.assertEqual(p1, pickled_period)

        os.unlink(f.name)
