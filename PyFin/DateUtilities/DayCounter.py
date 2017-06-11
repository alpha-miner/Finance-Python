# -*- coding: utf-8 -*-
u"""
Created on 2017-6-11

@author: cheng.li
"""

from PyFin.Enums.Months import Months


class DayCounter(object):

    def __init__(self, dcName):

        dcName = dcName.lower()
        if dcName in _dcDict:
            self.impl_ = _dcDict[dcName]()
        else:
            raise ValueError('{0} is not a valid day counter name'.format(dcName))

    def name(self):
        return self.impl_.name()

    def dayCount(self, d1, d2):
        return self.impl_.dayCount(d1, d2)

    def yearFraction(self, d1, d2, refPeriodStart, refPeriodEnd):
        return self.impl_.yearFraction(d1, d2, refPeriodStart, refPeriodEnd)


class DayCounterImpl(object):

    def name(self):
        pass

    def dayCount(self, d1, d2):
        return d2 - d1

    def yearFraction(self, d1, d2, refPeriodStart, refPeriodEnd):
        pass


class Actual360(DayCounterImpl):

    def name(self):
        return 'Actual/360'

    def yearFraction(self, d1, d2, refPeriodStart, refPeriodEnd2):
        return float(d2 - d1) / 360.


class Actual365Fixed(DayCounterImpl):

    def name(self):
        return 'Actual/365 (Fixed)'

    def yearFraction(self, d1, d2, refPeriodStart, refPeriodEnd2):
        return float(d2 - d1) / 365.


class Actual365NoLeap(DayCounterImpl):
    MonthOffset = [
        0, 31, 59, 90, 120, 151,  # Jan - Jun
        181, 212, 243, 273, 304, 334  # Jun - Dec
    ]

    def name(self):
        return 'Actual/365 (NL)'

    def dayCount(self, d1, d2):

        s1 = d1.dayOfMonth() + self.MonthOffset[d1.month() - 1] + (d1.year() * 365)
        s2 = d2.dayOfMonth() + self.MonthOffset[d2.month() - 1] + (d2.year() * 365)

        if d1.month() == Months.Feb and d1.dayOfMonth() == 29:
            s1 -= 1

        if d2.month() == Months.Feb and d2.dayOfMonth() == 29:
            s2 -= 1

        return s2 - s1

    def yearFraction(self, d1, d2, refPeriodStart, refPeriodEnd2):
        return self.dayCount(d1, d2) / 365.


_dcDict = {'actual/360': Actual360,
           'actual/365 (fixed)': Actual365Fixed,
           'actual/365 (nl)': Actual365NoLeap}
