# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

import unittest
import datetime as dt
from PyFin.DateUtilities import Date
from PyFin.DateUtilities import Period
from PyFin.Enums import Weekdays


class TestDate(unittest.TestCase):
    def testDateInputWithSerialNumber(self):
        serialNumber = 45678
        testDate = Date(serialNumber=serialNumber)
        self.assertEqual(testDate.serialNumber, serialNumber)

    def testDateInputWithSerialNumberAndNotNullYearMonthDay(self):
        serialNumber = 45678
        with self.assertRaises(ValueError):
            _ = Date(year=2015, serialNumber=serialNumber)

    def testDateInputWithoutCompleteInformationOnYearMonthDay(self):
        year = 2015
        month = None
        day = 18
        with self.assertRaises(ValueError):
            _ = Date(year=year, month=month, day=day)

    def testBasicFunctions(self):
        year = 2015
        month = 7
        day = 24
        strRepr = "{0}-{1:02d}-{2:02d}".format(year, month, day)
        innerRepr = "Date({0}, {1}, {2})".format(year, month, day)

        testDate = Date(year, month, day)
        self.assertEqual(str(testDate), strRepr, "date string:\n"
                                                 "expected:   {0:s}\n"
                                                 "calculated: {1:s}".format(strRepr, str(testDate)))

        self.assertEqual(repr(testDate), innerRepr, "date representation:\n"
                                                    "expected:   {0:s}\n"
                                                    "calculated: {1:s}".format(innerRepr, repr(testDate)))

        self.assertEqual(testDate.year(), year, "date year:\n"
                                                "expected:   {0:d}\n"
                                                "calculated: {1:d}".format(year, testDate.year()))

        self.assertEqual(testDate.month(), month, "date month:\n"
                                                  "expected:   {0:d}\n"
                                                  "calculated: {1:d}".format(month, testDate.month()))

        self.assertEqual(testDate.dayOfMonth(), day, "date day:\n"
                                                     "expected:   {0:d}\n"
                                                     "calculated: {1:d}".format(day, testDate.dayOfMonth()))

        self.assertEqual(testDate.dayOfYear(), testDate - Date(2015, 1, 1) + 1, "date day:\n"
                                                                                "expected:   {0:d}\n"
                                                                                "calculated: {1:d}"
                         .format(testDate - Date(2015, 1, 1) + 1, testDate.dayOfYear()))
        self.assertEqual(testDate.weekday(), 6, "date weekday:\n"
                                                "expected:   {0:d}\n"
                                                "calculated: {1:d}".format(5, testDate.weekday()))

        self.assertEqual(testDate.toDateTime(), dt.date(year, month, day), "date datetime representation\n"
                                                                           "expected:   {0}\n"
                                                                           "calculated: {1}".format(
            dt.datetime(year, month, day), testDate.toDateTime()))

        serialNumber = testDate.serialNumber
        serialDate = Date(serialNumber=serialNumber)

        self.assertEqual(serialDate, testDate, "date excel serial number representation\n"
                                               "expected:   {0:d}"
                                               "calculated: {1:d}".format(serialDate.serialNumber,
                                                                          testDate.serialNumber))

        # test comparisons
        previousDate = testDate - 1
        self.assertTrue(previousDate < testDate, "{0} is not earlier than {1}".format(previousDate, testDate))
        self.assertFalse(previousDate >= testDate,
                         "{0} should not be later than or equal to {1}".format(previousDate, testDate))
        self.assertTrue((previousDate + 1) == testDate,
                        "{0} plus one day should be equal to {1}".format(previousDate, testDate))

        # check static members
        self.assertEqual(Date.minDate(), Date(1901, 1, 1), "min date is wrong")
        self.assertEqual(Date.maxDate(), Date(2199, 12, 31), "max date is wrong")
        self.assertEqual(Date.endOfMonth(testDate), Date(year, month, 31), "end of month is wrong")
        self.assertTrue(Date.isEndOfMonth(Date(year, month, 31)), "{0} should be the end of month")
        self.assertEqual(Date.nextWeekday(testDate, testDate.weekday()), testDate,
                         "{0}'s next same week day should be {1}"
                         .format(testDate, testDate))
        self.assertEqual(Date.todaysDate().toDateTime(), dt.date.today(), "today's date\n"
                                                                          "expected:   {0}\n"
                                                                          "calculated: {1}".format(dt.date.today(),
                                                                                                   Date.todaysDate()))

        # nth-week day
        with self.assertRaises(ValueError):
            _ = Date.nthWeekday(0, Weekdays.Friday, 1, 2015)

        with self.assertRaises(ValueError):
            _ = Date.nthWeekday(6, Weekdays.Friday, 1, 2015)

        self.assertEqual(Date.nthWeekday(3, Weekdays.Wednesday, 8, 2015), Date(2015, 8, 19))

        # check plus/sub

        threeWeeksAfter = testDate + '3W'
        expectedDate = testDate + 21
        self.assertEqual(threeWeeksAfter, expectedDate, "date + 3w period\n"
                                                        "expected:   {0}\n"
                                                        "calculated: {1}".format(expectedDate, threeWeeksAfter))

        threeMonthsBefore = testDate - "3M"
        expectedDate = Date(year, month - 3, day)
        self.assertEqual(threeMonthsBefore, expectedDate, "date - 3m period\n"
                                                          "expected:   {0}\n"
                                                          "calculated: {1}".format(expectedDate, threeMonthsBefore))

        threeMonthsBefore = testDate - Period("3M")
        expectedDate = Date(year, month - 3, day)
        self.assertEqual(threeMonthsBefore, expectedDate, "date - 3m period\n"
                                                          "expected:   {0}\n"
                                                          "calculated: {1}".format(expectedDate, threeMonthsBefore))

        threeMonthsAfter = testDate + "3m"
        expectedDate = Date(year, month + 3, day)
        self.assertEqual(threeMonthsAfter, expectedDate, "date + 3m period\n"
                                                         "expected:   {0}\n"
                                                         "calculated: {1}".format(expectedDate, threeMonthsAfter))

        oneYearAndTwoMonthsBefore = testDate - "14m"
        expectedDate = Date(year - 1, month - 2, day)
        self.assertEqual(oneYearAndTwoMonthsBefore, expectedDate, "date - 14m period\n"
                                                                  "expected:   {0}\n"
                                                                  "calculated: {1}".format(expectedDate,
                                                                                           threeMonthsBefore))

        oneYearAndTwoMonthsBefore = testDate + "14m"
        expectedDate = Date(year + 1, month + 2, day)
        self.assertEqual(oneYearAndTwoMonthsBefore, expectedDate, "date + 14m period\n"
                                                                  "expected:   {0}\n"
                                                                  "calculated: {1}".format(expectedDate,
                                                                                           threeMonthsBefore))

        fiveMonthsAfter = testDate + "5m"
        expectedDate = Date(year, month + 5, day)
        self.assertEqual(fiveMonthsAfter, expectedDate, "date + 5m period\n"
                                                        "expected:   {0}\n"
                                                        "calculated: {1}".format(expectedDate, fiveMonthsAfter))

    def testConsistency(self):
        minDate = Date.minDate().serialNumber + 1
        maxDate = Date.maxDate().serialNumber

        dyold = Date.fromExcelSerialNumber(minDate - 1).dayOfYear()
        dold = Date.fromExcelSerialNumber(minDate - 1).dayOfMonth()
        mold = Date.fromExcelSerialNumber(minDate - 1).month()
        yold = Date.fromExcelSerialNumber(minDate - 1).year()
        wdold = Date.fromExcelSerialNumber(minDate - 1).weekday()

        for i in range(minDate, maxDate + 1):
            t = Date.fromExcelSerialNumber(i)
            serial = t.serialNumber
            self.assertEqual(serial, i, "inconsistent serial number:\n"
                                        "   original:      {0:d}\n"
                                        "   serial number: {1:d}".format(i, serial))

            dy = t.dayOfYear()
            d = t.dayOfMonth()
            m = t.month()
            y = t.year()
            wd = t.weekday()

            flag = (dy == dyold + 1) or \
                   (dy == 1 and dyold == 365 and not Date.isLeap(yold)) or \
                   (dy == 1 and dyold == 366 and Date.isLeap(yold))

            self.assertTrue(flag, "wrong day of year increment: \n"
                                  "    date: {0}\n"
                                  "    day of year: {1:d}\n"
                                  "    previous:    {2:d}".format(t, dy, dyold))

            dyold = dy

            flag = (d == dold + 1 and m == mold and y == yold) or \
                   (d == 1 and m == mold + 1 and y == yold) or \
                   (d == 1 and m == 1 and y == yold + 1)

            self.assertTrue(flag, "wrong day,month,year increment: \n"
                                  "    date: {0}\n"
                                  "    year,month,day: {1:d}, {2:d}, {3:d}\n"
                                  "    previous:       {4:d}, {5:d}, {6:d}".format(t, y, m, d, yold, mold, dold))
            dold = d
            mold = m
            yold = y

            self.assertTrue(d >= 1, "invalid day of month: \n"
                                    "    date:  {0}\n"
                                    "    day: {1:d}".format(t, d))

            flag = (m == 1 and d <= 31) or \
                   (m == 2 and d <= 28) or \
                   (m == 2 and d == 29 and Date.isLeap(y)) or \
                   (m == 3 and d <= 31) or \
                   (m == 4 and d <= 30) or \
                   (m == 5 and d <= 31) or \
                   (m == 6 and d <= 30) or \
                   (m == 7 and d <= 31) or \
                   (m == 8 and d <= 31) or \
                   (m == 9 and d <= 30) or \
                   (m == 10 and d <= 31) or \
                   (m == 11 and d <= 30) or \
                   (m == 12 and d <= 31)

            self.assertTrue(flag, "invalid day of month: \n"
                                  "    date:  {0}\n"
                                  "    day: {1:d}".format(t, d))

            flag = (wd == (wdold + 1)) or (wd == 1 or wdold == 7)

            self.assertTrue(flag, "invalid weekday: \n"
                                  "    date:  {0}\n"
                                  "    weekday:  {1:d}\n"
                                  "    previous: {2:d}".format(t, wd, wdold))
            wdold = wd

            s = Date(y, m, d)
            serial = s.serialNumber

            self.assertTrue(serial == i, "inconsistent serial number:\n"
                                         "    date:          {0}\n"
                                         "    serial number: {1:d}\n"
                                         "    cloned date:   {2}\n"
                                         "    serial number: {3:d}".format(t, i, s, serial))

    def testIsoDate(self):
        input_date = "2006-01-15"
        d = Date.parseISO(input_date)
        flag = d.dayOfMonth() == 15 and \
               d.month() == 1 and \
               d.year() == 2006

        self.assertTrue(flag, "Iso date failed\n"
                              " input date:    {0}\n"
                              " day of month:  {1:d}\n"
                              " month:         {2:d}\n"
                              " year:          {3:d}".format(input_date, d.dayOfMonth(), d.month(), d.year()))

    def testParseDates(self):
        input_date = "2006-01-15"
        d = Date.strptime(input_date, "%Y-%m-%d")
        flag = d == Date(2006, 1, 15)

        self.assertTrue(flag, "date parsing failed\n"
                              " input date:    {0:s}\n"
                              " parsed:        {1}".format(input_date, d))

        input_date = "12/02/2012"
        d = Date.strptime(input_date, "%m/%d/%Y")
        flag = d == Date(2012, 12, 2)

        self.assertTrue(flag, "date parsing failed\n"
                              " input date:    {0:s}\n"
                              " parsed:        {1}".format(input_date, d))

        d = Date.strptime(input_date, "%d/%m/%Y")
        flag = d == Date(2012, 2, 12)

        self.assertTrue(flag, "date parsing failed\n"
                              " input date:    {0:s}\n"
                              " parsed:        {1}".format(input_date, d))

        input_date = "20011002"
        d = Date.strptime(input_date, "%Y%m%d")
        flag = d == Date(2001, 10, 2)

        self.assertTrue(flag, "date parsing failed\n"
                              " input date:    {0:s}\n"
                              " parsed:        {1}".format(input_date, d))
