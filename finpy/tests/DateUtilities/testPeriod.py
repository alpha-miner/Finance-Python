# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

import unittest
from finpy.DateUtilities import Period
from finpy.Enums import TimeUnits

class TestPeriod(unittest.TestCase):

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