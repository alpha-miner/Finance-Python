# -*- coding: utf-8 -*-
u"""
Created on 2017-6-12

@author: cheng.li
"""

import unittest
from PyFin.DateUtilities.Date import Date
from PyFin.DateUtilities.Period import Period
from PyFin.DateUtilities.Calendar import Calendar
from PyFin.DateUtilities.Schedule import Schedule
from PyFin.DateUtilities.DayCounter import DayCounter


class SingleCase(object):
    def __init__(self, start, end, result, refStart=None, refEnd=None):
        self.start = start
        self.end = end
        self.refStart = refStart
        self.refEnd = refEnd
        self.result = result


class TestDayCounter(unittest.TestCase):
    def testActualActual(self):
        cases = [
            # first example
            SingleCase(Date(2003, 11, 1), Date(2004, 5, 1), 0.500000000000, Date(2003, 11, 1), Date(2004, 5, 1)),
            # short first calculation period(first period)
            SingleCase(Date(1999, 2, 1), Date(1999, 7, 1), 0.410958904110, Date(1998, 7, 1), Date(1999, 7, 1)),
            # short first calculation period(second period)
            SingleCase(Date(1999, 7, 1), Date(2000, 7, 1), 1.000000000000, Date(1999, 7, 1), Date(2000, 7, 1)),
            # long first calculation period(first period)
            SingleCase(Date(2002, 8, 15), Date(2003, 7, 15), 0.915760869565, Date(2003, 1, 15), Date(2003, 7, 15)),
            # long first calculation period(second period) / *Warning:
            # the ISDA case is in disagreement with mktc1198.pdf *
            SingleCase(Date(2003, 7, 15), Date(2004, 1, 15), 0.500000000000, Date(2003, 7, 15), Date(2004, 1, 15)),
            # short final calculation period(penultimate period)
            SingleCase(Date(1999, 7, 30), Date(2000, 1, 30), 0.500000000000, Date(1999, 7, 30), Date(2000, 1, 30)),
            # short final calculation period(final period)
            SingleCase(Date(2000, 1, 30), Date(2000, 6, 30), 0.417582417582, Date(2000, 1, 30), Date(2000, 7, 30))
        ]

        for case in cases:
            dayCounter = DayCounter('Actual/Actual (ISMA)')
            d1 = case.start
            d2 = case.end
            rd1 = case.refStart
            rd2 = case.refEnd

            calculated = dayCounter.yearFraction(d1, d2, rd1, rd2)
            self.assertAlmostEqual(case.result, calculated)


if __name__ == '__main__':
    unittest.main()