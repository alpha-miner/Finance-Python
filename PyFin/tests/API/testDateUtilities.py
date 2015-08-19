# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

import unittest
import datetime as dt
from PyFin.DateUtilities.Date import Date
from PyFin.DateUtilities.Calendar import Calendar
from PyFin.Enums.BizDayConventions import BizDayConventions
from PyFin.API.DateUtilities import datesList
from PyFin.API.DateUtilities import bizDatesList
from PyFin.API.DateUtilities import holDatesList
from PyFin.API.DateUtilities import advanceDate
from PyFin.API.DateUtilities import advanceDateByCalendar
from PyFin.API.DateUtilities import adjustDateByCalendar


class TestDateUtilities(unittest.TestCase):
    def setUp(self):

        self.fromDate = dt.date(2010, 1, 1)
        self.toDate = dt.date.today()

    def testDatesList(self):
        dtList = datesList(self.fromDate, self.toDate)
        fromDate = Date.fromDateTime(self.fromDate)

        for i, date in enumerate(dtList):
            expected = date
            calculated = (fromDate + i).toDateTime()
            self.assertEqual(date, (fromDate + i).toDateTime(), "at index {0:d}"
                                                                "expected:   {1}"
                                                                "calculated: {2}".format(i, expected, calculated))

    def testBizDatesList(self):
        bizDtList = bizDatesList('China.SSE', self.fromDate, self.toDate)
        fromDate = Date.fromDateTime(self.fromDate)
        currentDate = fromDate.toDateTime()
        cal = Calendar('China.SSE')
        while currentDate <= self.toDate:
            finpyDate = Date.fromDateTime(currentDate)
            if cal.isBizDay(finpyDate):
                self.assertTrue(finpyDate.toDateTime() in bizDtList,
                                "{0} is expected as a business day in {1}".format(finpyDate, cal))
            currentDate = (finpyDate + 1).toDateTime()

    def testHolDatesList(self):
        holDtList = holDatesList('China.SSE', self.fromDate, self.toDate)
        fromDate = Date.fromDateTime(self.fromDate)
        currentDate = fromDate.toDateTime()
        cal = Calendar('China.SSE')
        while currentDate <= self.toDate:
            finpyDate = Date.fromDateTime(currentDate)
            if not cal.isBizDay(finpyDate):
                self.assertTrue(finpyDate.toDateTime() in holDtList,
                                "{0} is expected as a holiday in {1}".format(finpyDate, cal))
            currentDate = (finpyDate + 1).toDateTime()

    def testAdvanceDate(self):
        referenceDate = dt.date.today()

        expected = advanceDate(referenceDate, '3M')
        calculated = Date.fromDateTime(referenceDate) + '3M'
        self.assertEqual(expected, calculated.toDateTime())

        expected = advanceDate(referenceDate, '-3M')
        calculated = Date.fromDateTime(referenceDate) - '3M'
        self.assertEqual(expected, calculated.toDateTime())

    def testAdjustDateByCalendar(self):
        referenceDate = Date(2014, 10, 1)
        cal = Calendar('China.SSE')

        expected = adjustDateByCalendar('China.SSE', referenceDate.toDateTime())
        calculated = cal.adjustDate(referenceDate)
        self.assertEqual(expected, calculated.toDateTime())

        referenceDate = Date(2014, 10, 8)
        expected = adjustDateByCalendar('China.SSE', referenceDate.toDateTime(), BizDayConventions.Preceding)
        calculated = cal.adjustDate(referenceDate, BizDayConventions.Preceding)
        self.assertEqual(expected, calculated.toDateTime())

    def testAdvanceDateByCalendar(self):
        referenceDate = Date(2014, 10, 1)
        cal = Calendar('China.SSE')

        expected = advanceDateByCalendar('China.SSE', referenceDate.toDateTime(), '2D')
        calculated = cal.advanceDate(referenceDate, '2D')
        self.assertEqual(expected, calculated.toDateTime())

        expected = advanceDateByCalendar('China.SSE', referenceDate.toDateTime(), '2D')
        calculated = cal.advanceDate(referenceDate, '2D')
        self.assertEqual(expected, calculated.toDateTime())

        expected = advanceDateByCalendar('China.SSE', referenceDate.toDateTime(), '2B')
        calculated = cal.advanceDate(referenceDate, '2B')
        self.assertEqual(expected, calculated.toDateTime())

        expected = advanceDateByCalendar('China.SSE', referenceDate.toDateTime(), '1Y')
        calculated = cal.advanceDate(referenceDate, '1Y')
        self.assertEqual(expected, calculated.toDateTime())
