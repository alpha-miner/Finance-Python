# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

import unittest
from PyFin.DateUtilities import Period
from PyFin.Enums import TimeUnits


class TestPeriod(unittest.TestCase):
    def testBasicArithmic(self):
        # test bad normalize
        testPriod = Period(1, TimeUnits.Years)
        testPriod._units = 10
        with self.assertRaises(TypeError):
            testPriod.normalize()

        # test plus method
        p1 = Period(0, TimeUnits.Days)
        p2 = Period(10, TimeUnits.Months)
        calculated = p1 + p2
        self.assertEqual(p2, calculated, "added value {0} should be equal to {1}".format(calculated, p2))

        p1 = Period(2, TimeUnits.Years)
        p2 = Period(13, TimeUnits.Months)
        calculated = p1 + p2
        expected = Period(37, TimeUnits.Months)
        self.assertEqual(expected, calculated, "added value {0} should be equal to {1}".format(calculated, expected))

        p2 = Period(2, TimeUnits.Weeks)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.Days)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p1 = Period(13, TimeUnits.Months)
        p2 = Period(2, TimeUnits.Years)
        calculated = p1 + p2
        expected = Period(37, TimeUnits.Months)
        self.assertEqual(expected, calculated, "added value {0} should be equal to {1}".format(calculated, expected))

        p2 = Period(2, TimeUnits.Weeks)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.Days)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p1 = Period(2, TimeUnits.Weeks)
        p2 = Period(7, TimeUnits.Days)
        calculated = p1 + p2
        expected = Period(21, TimeUnits.Days)
        self.assertEqual(expected, calculated, "added value {0} should be equal to {1}".format(calculated, expected))

        p2 = Period(2, TimeUnits.Months)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.Years)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p1 = Period(7, TimeUnits.Days)
        p2 = Period(2, TimeUnits.Weeks)
        calculated = p1 + p2
        expected = Period(21, TimeUnits.Days)
        self.assertEqual(expected, calculated, "added value {0} should be equal to {1}".format(calculated, expected))

        p2 = Period(2, TimeUnits.Months)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.Years)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p1 = Period(7, TimeUnits.BDays)

        p2 = Period(2, TimeUnits.Months)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.Days)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.Weeks)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.Years)
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2._units = 10
        with self.assertRaises(ValueError):
            _ = p1 + p2

        p2 = Period(2, TimeUnits.BDays)
        self.assertEqual(p1 + p2, Period('9B'))

        # test negative operator
        p1 = Period(-13, TimeUnits.Weeks)
        p2 = -p1
        self.assertEqual(p2, Period(13, TimeUnits.Weeks))

        # test less operator
        p1 = Period(0, TimeUnits.Days)
        p2 = Period(-3, TimeUnits.BDays)
        self.assertTrue(p2 < p1)

        # test sub operator
        p1 = Period(0, TimeUnits.Days)
        p2 = Period(-3, TimeUnits.BDays)
        self.assertEqual(p1 - p2, Period('3b'))

        # test string representation
        p1 = Period(12, TimeUnits.Months)
        self.assertEqual("1Y", p1.__str__())

    def testComparingOperators(self):
        p1 = Period(0, TimeUnits.Days)
        p2 = Period(1, TimeUnits.Days)
        self.assertTrue(p1 < p2)

        p1 = Period(13, TimeUnits.Months)
        p2 = Period(1, TimeUnits.Years)
        self.assertTrue(not p1 < p2)

        p1 = Period(1, TimeUnits.Years)
        p2 = Period(13, TimeUnits.Months)
        self.assertTrue(p1 < p2)

        p1 = Period(13, TimeUnits.Days)
        p2 = Period(2, TimeUnits.Weeks)
        self.assertTrue(p1 < p2)

        p1 = Period(2, TimeUnits.Weeks)
        p2 = Period(13, TimeUnits.Days)
        self.assertTrue(not p1 < p2)

        p1 = Period(1, TimeUnits.Years)
        p2 = Period(56, TimeUnits.Weeks)
        self.assertTrue(p1 < p2)

        p1 = Period(56, TimeUnits.Weeks)
        p2 = Period(1, TimeUnits.Years)
        self.assertTrue(not p1 < p2)

        p1 = Period(21, TimeUnits.Weeks)
        p2 = Period(5, TimeUnits.Months)

        with self.assertRaises(ValueError):
            _ = p1 < p2

        p1 = Period(21, TimeUnits.BDays)
        with self.assertRaises(ValueError):
            _ = p1 < p2

        # test not equal operator
        p1 = Period(1, TimeUnits.Days)
        p2 = Period(1, TimeUnits.Days)
        self.assertTrue(not p1 != p2)

        p2 = Period(1, TimeUnits.Years)
        self.assertTrue(p1 != p2)

        # test greater than operator
        p1 = Period(1, TimeUnits.Days)
        p2 = Period(2, TimeUnits.Days)
        self.assertEqual(p1 < p2, not p1 > p2)

    def testYearsMonthsAlgebra(self):
        oneYear = Period(1, TimeUnits.Years)
        sixMonths = Period(6, TimeUnits.Months)
        threeMonths = Period(3, TimeUnits.Months)

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
        flag = sum == Period(9, TimeUnits.Months)
        self.assertTrue(flag, "sum error: {0}"
                              " + {1}"
                              " != {2}".format(threeMonths, sixMonths, Period(9, TimeUnits.Months)))

        sum += oneYear
        flag = sum == Period(21, TimeUnits.Months)
        self.assertTrue(flag, "sum error: {0}"
                              " + {1}"
                              " + {2}"
                              " != {3}".format(threeMonths, sixMonths, oneYear, Period(21, TimeUnits.Months)))

        twelveMonths = Period(12, TimeUnits.Months)
        flag = twelveMonths.length == 12
        self.assertTrue(flag, "normalization error: TwelveMonths.length"
                              " is {0:d}"
                              " instead of 12".format(twelveMonths.length))
        flag = twelveMonths.units == TimeUnits.Months
        self.assertTrue(flag, "normalization error: TwelveMonths.units"
                              " is {0:d}"
                              " instead of {1:d}".format(twelveMonths.units, TimeUnits.Months))

        normalizedTwelveMonths = Period(12, TimeUnits.Months)
        normalizedTwelveMonths = normalizedTwelveMonths.normalize()
        flag = normalizedTwelveMonths.length == 1
        self.assertTrue(flag, "normalization error: TwelveMonths.length"
                              " is {0:d}"
                              " instead of 1".format(twelveMonths.length))
        flag = normalizedTwelveMonths.units == TimeUnits.Years
        self.assertTrue(flag, "normalization error: TwelveMonths.units"
                              " is {0:d}"
                              " instead of {1:d}".format(twelveMonths.units, TimeUnits.Years))

        thirtyDays = Period(30, TimeUnits.Days)
        normalizedThirtyDays = thirtyDays.normalize()
        flag = normalizedThirtyDays.units == TimeUnits.Days
        self.assertTrue(flag, "normalization error: ThirtyDays.units"
                              " is {0:d}"
                              " instead of {1:d}".format(normalizedThirtyDays.units, TimeUnits.Days))

        thirtyBDays = Period(30, TimeUnits.BDays)
        normalizedThirtyBDays = thirtyBDays.normalize()
        flag = normalizedThirtyBDays.units == TimeUnits.BDays
        self.assertTrue(flag, "normalization error: ThirtyBDays.units"
                              " is {0:d}"
                              " instead of {1:d}".format(normalizedThirtyBDays.units, TimeUnits.BDays))

    def testWeeksDaysAlgebra(self):
        twoWeeks = Period(2, TimeUnits.Weeks)
        oneWeek = Period(1, TimeUnits.Weeks)
        threeDays = Period(3, TimeUnits.Days)
        oneDay = Period(1, TimeUnits.Days)

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
        flag = sum == Period(4, TimeUnits.Days)
        self.assertTrue(flag, "sum error: {0}"
                              " + {1}"
                              " != {2}".format(threeDays, oneDay, Period(4, TimeUnits.Days)))

        sum += oneWeek
        flag = sum == Period(11, TimeUnits.Days)
        self.assertTrue(flag, "sum error: {0}"
                              " + {1}"
                              " + {2}"
                              " != {3}".format(threeDays, oneDay, oneWeek, Period(11, TimeUnits.Days)))

        sevenDays = Period(7, TimeUnits.Days)
        flag = sevenDays.length == 7
        self.assertTrue(flag, "normalization error: sevenDays.length"
                              " is {0:d}"
                              " instead of 7".format(sevenDays.length))
        flag = sevenDays.units == TimeUnits.Days
        self.assertTrue(flag, "normalization error: sevenDays.units"
                              " is {0:d}"
                              " instead of {1:d}".format(sevenDays.units, TimeUnits.Days))

        normalizedSevenDays = sevenDays.normalize()
        flag = normalizedSevenDays.length == 1
        self.assertTrue(flag, "normalization error: normalizedSevenDays.length"
                              " is {0:d}"
                              " instead of 1".format(normalizedSevenDays.length))
        flag = normalizedSevenDays.units == TimeUnits.Weeks
        self.assertTrue(flag, "normalization error: TwelveMonths.units"
                              " is {0:d}"
                              " instead of {1:d}".format(normalizedSevenDays.units, TimeUnits.Weeks))
