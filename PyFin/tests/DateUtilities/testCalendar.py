# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

import unittest
from PyFin.DateUtilities import Date
from PyFin.DateUtilities import Calendar
from PyFin.Enums import BizDayConventions
from PyFin.Enums import Months
from PyFin.Enums import Weekdays


class TestCalendar(unittest.TestCase):
    def testWrongInputOfHolidayCenter(self):
        with self.assertRaises(ValueError):
            _ = Calendar('NulCalendar')

        with self.assertRaises(ValueError):
            _ = Calendar(Date(2015, 1, 1))

    def testCalendarConstructionIsInsensitiveOfCase(self):
        cal1 = Calendar('NullCalendar')
        cal2 = Calendar('nullcalendar')
        shouldBeTrue = cal1 == cal2
        self.assertTrue(shouldBeTrue)

        caltoBeDifferent = Calendar('China.SSE')
        shouldBeFalse = cal1 == caltoBeDifferent
        self.assertFalse(shouldBeFalse)

    def testBasicFunctions(self):

        testDate = Date(2015, 7, 11)
        cal = Calendar('China.SSE')
        self.assertTrue(cal.isWeekEnd(testDate.weekday()), "{0} is expected to be a weekend".format(testDate))
        testDate = Date(2015, 7, 13)
        self.assertTrue(not cal.isWeekEnd(testDate.weekday()), "{0} is expected not to be a weekend".format(testDate))

        testDate = Date(2015, 5, 29)
        cal = Calendar('China.SSE')
        self.assertTrue(cal.isEndOfMonth(testDate), "{0} is expected to be a end of month".format(testDate))

        testDate = Date(2015, 5, 1)
        cal = Calendar('China.SSE')
        endOfMonth = cal.endOfMonth(testDate)
        self.assertEqual(endOfMonth, Date(2015, 5, 29),
                         "The month end of 2015/5 is expected to be {0}".format(Date(2015, 5, 29)))

        bizDates1 = cal.bizDaysBetween(Date(2015, 1, 1), Date(2015, 12, 31), True, False)
        bizDates2 = cal.bizDaysBetween(Date(2015, 12, 31), Date(2015, 1, 1), False, True)
        self.assertEqual(bizDates1, bizDates2)

    def testNullCalendar(self):
        cal = Calendar("Null")

        testDate = Date(2015, 1, 1)
        self.assertTrue(cal.isBizDay(testDate))
        self.assertTrue(not cal.isHoliday(testDate))
        self.assertTrue(cal.isWeekEnd(Weekdays.Saturday))
        self.assertTrue(cal.isWeekEnd(Weekdays.Sunday))
        self.assertTrue(not cal.isWeekEnd(Weekdays.Friday))

    def testChinaSSE(self):
        # China Shhanghai Securities Exchange holiday list in the year 2014
        expectedHol = [Date(2014, 1, 1), Date(2014, 1, 31),
                       Date(2014, 2, 1), Date(2014, 2, 2), Date(2014, 2, 3), Date(2014, 2, 4), Date(2014, 2, 5),
                       Date(2014, 2, 6), Date(2014, 2, 8),
                       Date(2014, 4, 5), Date(2014, 4, 6), Date(2014, 4, 7),
                       Date(2014, 5, 1), Date(2014, 5, 2), Date(2014, 5, 3), Date(2014, 5, 4), Date(2014, 5, 31),
                       Date(2014, 6, 1), Date(2014, 6, 2),
                       Date(2014, 9, 6), Date(2014, 9, 7), Date(2014, 9, 8), Date(2014, 9, 28),
                       Date(2014, 10, 1), Date(2014, 10, 2), Date(2014, 10, 3), Date(2014, 10, 4), Date(2014, 10, 5),
                       Date(2014, 10, 6), Date(2014, 10, 7), Date(2014, 10, 11),
                       # China Shhanghai Securities Exchange holiday list in the year 2015
                       Date(2015, 1, 1), Date(2015, 1, 2), Date(2015, 1, 3), Date(2015, 1, 4),
                       Date(2015, 2, 15), Date(2015, 2, 18), Date(2015, 2, 19), Date(2015, 2, 20), Date(2015, 2, 21),
                       Date(2015, 2, 22), Date(2015, 2, 23), Date(2015, 2, 24), Date(2015, 2, 28),
                       Date(2015, 4, 5), Date(2015, 4, 6),
                       Date(2015, 5, 1), Date(2015, 5, 2), Date(2015, 5, 3),
                       Date(2015, 6, 20), Date(2015, 6, 21), Date(2015, 6, 22),
                       Date(2015, 9, 3), Date(2015, 9, 4), Date(2015, 9, 27),
                       Date(2015, 10, 1), Date(2015, 10, 2), Date(2015, 10, 3), Date(2015, 10, 4), Date(2015, 10, 5),
                       Date(2015, 10, 6), Date(2015, 10, 7), Date(2015, 10, 10)]

        cal = Calendar('China.SSE')

        for day in expectedHol:
            self.assertEqual(cal.isHoliday(day), True, "{0} is expected to be a holiday in {1}".format(day, cal))
            self.assertEqual(cal.isBizDay(day), False,
                             "{0} is expected not to be a working day in {1} ".format(day, cal))

    def testChinaIB(self):

        # China Inter Bank working weekend list in the year 2014
        expectedWorkingWeekEnd = [Date(2014, 1, 26),
                                  Date(2014, 2, 8),
                                  Date(2014, 5, 4),
                                  Date(2014, 9, 28),
                                  Date(2014, 10, 11),
                                  # China Inter Bank working weekend list in the year 2015
                                  Date(2015, 1, 4),
                                  Date(2015, 2, 15),
                                  Date(2015, 2, 28),
                                  Date(2015, 9, 6),
                                  Date(2015, 10, 10)]

        cal = Calendar('China.IB')

        for day in expectedWorkingWeekEnd:
            self.assertEqual(cal.isHoliday(day), False, "{0} is not expected to be a holiday in {1}".format(day, cal))
            self.assertEqual(cal.isBizDay(day), True, "{0} is expected to be a working day in {1} ".format(day, cal))

    def testAdjustDate(self):
        # April 30, 2005 is a working day under IB, but a holiday under SSE
        referenceDate = Date(2005, Months.April, 30)

        sseCal = Calendar('China.SSE')
        ibCal = Calendar('China.IB')

        bizDayConv = BizDayConventions.Unadjusted
        self.assertEqual(sseCal.adjustDate(referenceDate, bizDayConv), referenceDate)
        self.assertEqual(ibCal.adjustDate(referenceDate, bizDayConv), referenceDate)

        bizDayConv = BizDayConventions.Following
        self.assertEqual(sseCal.adjustDate(referenceDate, bizDayConv), Date(2005, Months.May, 9))
        self.assertEqual(ibCal.adjustDate(referenceDate, bizDayConv), Date(2005, Months.April, 30))

        bizDayConv = BizDayConventions.ModifiedFollowing
        self.assertEqual(sseCal.adjustDate(referenceDate, bizDayConv), Date(2005, Months.April, 29))
        self.assertEqual(ibCal.adjustDate(referenceDate, bizDayConv), Date(2005, Months.April, 30))

    def testAdvanceDate(self):
        referenceDate = Date(2014, 1, 31)
        sseCal = Calendar('China.SSE')
        ibCal = Calendar('China.IB')

        bizDayConv = BizDayConventions.Following

        # test null period
        self.assertEqual(sseCal.advanceDate(referenceDate, '0b', bizDayConv), Date(2014, 2, 7))

        # test negative period
        self.assertEqual(sseCal.advanceDate(referenceDate, '-5b', bizDayConv), Date(2014, 1, 24))

        # The difference is caused by Feb 8 is SSE holiday but a working day for IB market
        self.assertEqual(sseCal.advanceDate(referenceDate, '2b', bizDayConv), Date(2014, 2, 10))
        self.assertEqual(sseCal.advanceDate(referenceDate, '2d', bizDayConv), Date(2014, 2, 7))
        self.assertEqual(ibCal.advanceDate(referenceDate, '2b', bizDayConv), Date(2014, 2, 8))
        self.assertEqual(ibCal.advanceDate(referenceDate, '2d', bizDayConv), Date(2014, 2, 7))

        bizDayConv = BizDayConventions.ModifiedFollowing
        # May 31, 2014 is a holiday
        self.assertEqual(sseCal.advanceDate(referenceDate, '4m', bizDayConv, True), Date(2014, 5, 30))

    def testDatesList(self):

        fromDate = Date(2014, 1, 31)
        toDate = Date(2014, 2, 28)
        sseCal = Calendar('China.SSE')
        ibCal = Calendar('China.IB')

        benchmarkHol = [Date(2014, 1, 31), Date(2014, 2, 3), Date(2014, 2, 4), Date(2014, 2, 5), Date(2014, 2, 6)]
        sseHolList = sseCal.holDatesList(fromDate, toDate, False)
        self.assertEqual(sseHolList, benchmarkHol)
        ibHolList = ibCal.holDatesList(fromDate, toDate, False)
        self.assertEqual(ibHolList, benchmarkHol)

        sseHolList = sseCal.holDatesList(fromDate, toDate, True)
        benchmarkHol = [Date(2014, 1, 31), Date(2014, 2, 1), Date(2014, 2, 2), Date(2014, 2, 3), Date(2014, 2, 4),
                        Date(2014, 2, 5), Date(2014, 2, 6), Date(2014, 2, 8), Date(2014, 2, 9), Date(2014, 2, 15),
                        Date(2014, 2, 16), Date(2014, 2, 22), Date(2014, 2, 23)]
        self.assertEqual(sseHolList, benchmarkHol)
        ibHolList = ibCal.holDatesList(fromDate, toDate, True)
        benchmarkHol = [Date(2014, 1, 31), Date(2014, 2, 1), Date(2014, 2, 2), Date(2014, 2, 3), Date(2014, 2, 4),
                        Date(2014, 2, 5), Date(2014, 2, 6), Date(2014, 2, 9), Date(2014, 2, 15), Date(2014, 2, 16),
                        Date(2014, 2, 22), Date(2014, 2, 23)]
        self.assertEqual(ibHolList, benchmarkHol)

        sseWorkingDayList = sseCal.bizDatesList(fromDate, toDate)
        d = fromDate
        while d <= toDate:
            if sseCal.isBizDay(d):
                self.assertTrue(d in sseWorkingDayList and d not in sseHolList)
            d += 1

        ibWorkingDayList = ibCal.bizDatesList(fromDate, toDate)
        d = fromDate
        while d <= toDate:
            if ibCal.isBizDay(d):
                self.assertTrue(d in ibWorkingDayList and d not in ibHolList)
            d += 1

    def testCalendarWithDayConvention(self):
        sseCal = Calendar('China.SSE')

        referenceDate = Date(2015, 2, 14)
        testDate = sseCal.adjustDate(referenceDate, BizDayConventions.HalfMonthModifiedFollowing)
        self.assertEqual(testDate, Date(2015, 2, 13))

        referenceDate = Date(2014, 2, 4)
        testDate = sseCal.adjustDate(referenceDate, BizDayConventions.ModifiedPreceding)
        self.assertEqual(testDate, Date(2014, 2, 7))

        referenceDate = Date(2014, 2, 3)
        testDate = sseCal.adjustDate(referenceDate, BizDayConventions.Nearest)
        self.assertEqual(testDate, Date(2014, 2, 7))

        referenceDate = Date(2014, 2, 2)
        testDate = sseCal.adjustDate(referenceDate, BizDayConventions.Nearest)
        self.assertEqual(testDate, Date(2014, 1, 30))

        with self.assertRaises(ValueError):
            _ = sseCal.adjustDate(referenceDate, -1)
