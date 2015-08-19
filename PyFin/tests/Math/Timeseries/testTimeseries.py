# -*- coding: utf-8 -*-
u"""
Created on 2015-7-21

@author: cheng.li
"""

import unittest
from PyFin.DateUtilities.Date import Date
from PyFin.DateUtilities.Calendar import Calendar
from PyFin.Math.Timeseries import Timeseries


class TestTimeseries(unittest.TestCase):
    def testTimeseries(self):
        cal = Calendar('China.SSE')
        dates = cal.bizDatesList(Date(2014, 1, 1), Date(2015, 7, 21))
        values = [0.1 * i for i, _ in enumerate(dates)]

        ts = Timeseries(dates, values)

        self.assertEqual(ts.size(), len(dates))

        firstDate = ts.firstDate()
        lastDate = ts.lastDate()
        self.assertEqual(dates[0], firstDate, "Expected first date {0} is not equal to ts's first date {1}"
                         .format(dates[0], firstDate))
        self.assertEqual(dates[-1], lastDate, "Expected last date {0} is not equal to ts's last date {1}"
                         .format(dates[-1], lastDate))

        for date, value in zip(dates, values):
            self.assertEqual(ts[date], value, "Expected value at day {0} is not equal to expected {1:f}"
                             .format(date, value))
