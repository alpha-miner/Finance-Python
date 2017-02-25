# -*- coding: utf-8 -*-
u"""
Created on 2015-7-15

@author: cheng.li
"""

import unittest
import copy
import tempfile
import pickle
import os
from PyFin.DateUtilities import Date
from PyFin.DateUtilities import Schedule
from PyFin.DateUtilities import Period
from PyFin.DateUtilities import Calendar
from PyFin.Enums import TimeUnits
from PyFin.Enums import BizDayConventions


class TestSchedule(unittest.TestCase):
    def checkDates(self, s, expected):
        if s.size() != len(expected):
            self.fail("expected {0:d} dates, found {1}".format(len(expected), s.size()))

        for i in range(s.size()):
            if s[i] != expected[i]:
                self.fail("expected {0} at index found {1}".format(expected[i], s[i]))

    def testScheduleInitialize(self):
        startDate = Date(2013, 3, 31)
        endDate = Date(2013, 6, 30)
        tenor = Period('1m')
        cal = Calendar('NullCalendar')
        sch = Schedule(startDate, endDate, tenor, cal)
        expected = [Date(2013, 3, 31), Date(2013, 4, 30), Date(2013, 5, 31), Date(2013, 6, 30)]
        for i in range(sch.size()):
            self.assertEqual(expected[i], sch[i])

    def testScheduleInitializeWithYearly(self):
        startDate = Date(2012, 2, 29)
        endDate = Date(2013, 3, 1)
        tenor = Period('1y')
        cal = Calendar('NullCalendar')
        sch = Schedule(startDate, endDate, tenor, cal)
        expected = [Date(2012, 2, 29), Date(2013, 2, 28), Date(2013, 3, 1)]
        for i in range(sch.size()):
            self.assertEqual(expected[i], sch[i])

    def testDailySchedule(self):
        # Jan 2 and Jan 3 are skipped as New Year holiday
        # Jan 7 is skipped as weekend
        # Jan 8 is adjusted to Jan 9 with following convention
        startDate = Date(2012, 1, 1)
        s = Schedule(startDate,
                     startDate + 7,
                     Period(length=1, units=TimeUnits.Days),
                     Calendar("China.SSE"),
                     BizDayConventions.Preceding)

        expected = [Date(2011, 12, 30), Date(2012, 1, 4), Date(2012, 1, 5), Date(2012, 1, 6), Date(2012, 1, 9)]
        self.checkDates(s, expected)

        # The schedule should skip Saturday 21st and Sunday 22rd.
        # Previously, it would adjust them to Friday 20th, resulting
        # in three copies of the same date.
        startDate = Date(2012, 1, 17)
        s = Schedule(startDate,
                     startDate + 7,
                     Period(length=1, units=TimeUnits.Days),
                     Calendar("Target"),
                     BizDayConventions.Preceding)
        expected = [Date(2012, 1, 17), Date(2012, 1, 18), Date(2012, 1, 19), Date(2012, 1, 20), Date(2012, 1, 23),
                    Date(2012, 1, 24)]
        self.checkDates(s, expected)

    def testScheduleDeepCopy(self):
        startDate = Date(2013, 3, 31)
        endDate = Date(2013, 6, 30)
        tenor = Period('1m')
        cal = Calendar('NullCalendar')
        sch = Schedule(startDate, endDate, tenor, cal)
        copied_sch = copy.deepcopy(sch)

        self.assertEqual(sch, copied_sch)

    def testSchedulePickle(self):
        startDate = Date(2013, 3, 31)
        endDate = Date(2013, 6, 30)
        tenor = Period('1m')
        cal = Calendar('NullCalendar')
        sch = Schedule(startDate, endDate, tenor, cal)

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(sch, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled_sch = pickle.load(f2)
            self.assertEqual(sch, pickled_sch)

        os.unlink(f.name)
