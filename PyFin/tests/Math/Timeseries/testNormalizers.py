# -*- coding: utf-8 -*-
u"""
Created on 2015-7-21

@author: cheng.li
"""

import unittest
from PyFin.DateUtilities.Date import Date
from PyFin.Enums.NormalizingType import NormalizingType
from PyFin.Math.Timeseries.Normalizers import Normalizer
from PyFin.DateUtilities.Calendar import Calendar


class TestNormalizers(unittest.TestCase):
    def setUp(self):
        cal = Calendar('China.SSE')
        self.dates = cal.bizDatesList(Date(2014, 1, 1), Date(2015, 7, 21))
        self.rets = [0.05 for _ in self.dates]

    def testNullNormalizer(self):
        normalizer = Normalizer(NormalizingType.Null)
        for ret, date in zip(self.rets, self.dates):
            normalizedReturn = normalizer.normalizeOneDayReturn(date, ret)
            self.assertAlmostEqual(normalizedReturn, ret, 10, "Expected return {0:f} is not equal to normalized {1:f}"
                                   .format(ret, normalizedReturn))

    def testCalendarDayNormalizer(self):
        normalizer = Normalizer(NormalizingType.CalendarDay)
        for i, (ret, date) in enumerate(zip(self.rets, self.dates)):
            normalizedReturn = normalizer.normalizeOneDayReturn(date, ret)
            if i != 0:
                daysBetween = date - self.previous
            else:
                daysBetween = 1

            self.assertAlmostEqual(normalizedReturn, ret / daysBetween, 10,
                                   "Expected return {0:f} is not equal to normalized {1:f}"
                                   .format(ret / daysBetween, normalizedReturn))
            self.previous = date

    def testBizDayNormalizer(self):
        normalizer = Normalizer(NormalizingType.BizDay)
        for ret, date in zip(self.rets, self.dates):
            # as the dates are generated from SSE calendar
            # the biz days between should always be 1
            normalizedReturn = normalizer.normalizeOneDayReturn(date, ret)
            self.assertAlmostEqual(normalizedReturn, ret, 10, "Expected return {0:f} is not equal to normalized {1:f}"
                                   .format(ret, normalizedReturn))
