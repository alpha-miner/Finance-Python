# -*- coding: utf-8 -*-
u"""
Created on 2015-7-9

@author: cheng.li
"""

import re
import math
from copy import deepcopy
from PyFin.Enums.TimeUnits import TimeUnits
from PyFin.Utilities import pyFinAssert

_unitPattern = re.compile('[BbDdMmWwYy]{1}')
_numberPattern = re.compile('[-+]*[0-9]+')

_unitsDict = {'d': TimeUnits.Days,
              'b': TimeUnits.BDays,
              'w': TimeUnits.Weeks,
              'm': TimeUnits.Months,
              'y': TimeUnits.Years}


class Period(object):
    def __init__(self, *args):

        if isinstance(args[0], str):
            perStr = args[0]
            unitsPos = _unitPattern.search(perStr)
            numPos = _numberPattern.search(perStr)
            units = perStr[unitsPos.start():unitsPos.end()].lower()
            n = int(perStr[numPos.start():numPos.end()])
            self._length = n
            self._units = _unitsDict[units]
        elif isinstance(args[0], int) and isinstance(args[1], TimeUnits):
            self._length = args[0]
            self._units = args[1]

    @property
    def length(self):
        return self._length

    @property
    def units(self):
        return self._units

    def normalize(self):
        length = self.length
        units = self.units
        if self.length != 0:
            if self.units == TimeUnits.BDays or self.units == TimeUnits.Weeks or self.units == TimeUnits.Years:
                return deepcopy(self)
            elif self.units == TimeUnits.Months:
                if self.length % 12 == 0:
                    length = self.length // 12
                    units = TimeUnits.Years
                return Period(length, units)
            elif self.units == TimeUnits.Days:
                if self.length % 7 == 0:
                    length = self.length // 7
                    units = TimeUnits.Weeks
                return Period(length, units)
            else:
                raise TypeError("unknown time unit ({0:d})".format(self.units))

    def __div__(self, n):
        pyFinAssert(n != 0, ValueError, "cannot be divided by zero")

        res = Period(self.length, self.units)
        if self.length % n == 0:
            res._length /= n
        else:
            units = res.units
            length = res.length

            if units == TimeUnits.Years:
                length *= 12
                units = TimeUnits.Months
            elif units == TimeUnits.Weeks:
                length *= 7
                units = TimeUnits.Days

            pyFinAssert(length % n == 0, ValueError, "{0} cannot be divided by {1:d}".format(res, n))

            res._length = length / n
            res._units = units

        return res

    # only work for python 3
    def __truediv__(self, n):
        return self.__div__(n)

    def __add__(self, p2):
        res = Period(self.length, self.units)

        if self.length == 0:
            return Period(p2.length, p2.units)
        elif self.units == p2.units:
            res._length += p2.length
            return res
        else:
            if self.units == TimeUnits.Years:
                if p2.units == TimeUnits.Months:
                    res._units = TimeUnits.Months
                    res._length = res.length * 12 + p2.length
                elif p2.units == TimeUnits.Weeks or p2.units == TimeUnits.Days or p2.units == TimeUnits.BDays:
                    pyFinAssert(p2.length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2.units))
                return res
            elif self.units == TimeUnits.Months:
                if p2.units == TimeUnits.Years:
                    res._length += 12 * p2.length
                elif p2.units == TimeUnits.Weeks or p2.units == TimeUnits.Days or p2.units == TimeUnits.BDays:
                    pyFinAssert(p2.length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2.units))
                return res
            elif self.units == TimeUnits.Weeks:
                if p2.units == TimeUnits.Days:
                    res._units = TimeUnits.Days
                    res._length = res.length * 7 + p2.length
                elif p2.units == TimeUnits.Years or p2.units == TimeUnits.Months or p2.units == TimeUnits.BDays:
                    pyFinAssert(p2.length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2.units))
                return res
            elif self.units == TimeUnits.Days:
                if p2.units == TimeUnits.Weeks:
                    res._length += 7 * p2.length
                elif p2.units == TimeUnits.Years or p2.units == TimeUnits.Months or p2.units == TimeUnits.BDays:
                    pyFinAssert(p2.length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2.units))
                return res
            elif self.units == TimeUnits.BDays:
                if p2.units == TimeUnits.Years or p2.units == TimeUnits.Months or p2.units == TimeUnits.Weeks or p2.units == TimeUnits.Days:
                    pyFinAssert(p2.length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2.units))

    def __neg__(self):
        return Period(-self.length, self.units)

    def __sub__(self, p2):
        return self + (-p2)

    def __lt__(self, p2):

        if self.length == 0:
            return p2.length > 0

        if p2.length == 0:
            return self.length < 0

        # exact comparisons
        if self.units == p2.units:
            return self.length < p2.length
        elif self.units == TimeUnits.Months and p2.units == TimeUnits.Years:
            return self.length < (p2.length * 12)
        elif self.units == TimeUnits.Years and p2.units == TimeUnits.Months:
            return (self.length * 12) < p2.length
        elif self.units == TimeUnits.Days and p2.units == TimeUnits.Weeks:
            return self.length < (p2.length * 7)
        elif self.units == TimeUnits.Weeks and p2.units == TimeUnits.Days:
            return (self.length * 7) < p2.length

        # inexact comparisons (handled by converting to days and using limits)

        p1lim = _daysMinMax(self)
        p2lim = _daysMinMax(p2)

        if p1lim[1] < p2lim[0]:
            return True
        elif p1lim[0] >= p2lim[1]:
            return False
        else:
            raise ValueError("undecidable comparison between {0} and {1}".format(self, p2))

    def __eq__(self, p2):
        return not (self < p2 or p2 < self)

    def __ne__(self, p2):
        return not self == p2

    def __gt__(self, p2):
        return p2 < self

    def __str__(self):
        out = ""
        n = self.length
        m = 0

        if self.units == TimeUnits.Days:
            if n >= 7:
                m = int(math.floor(n / 7))
                out += str(m) + "W"
                n %= 7
            if n != 0 or m == 0:
                return out + str(n) + "D"
            else:
                return out
        elif self.units == TimeUnits.Weeks:
            return out + str(n) + "W"
        elif self.units == TimeUnits.Months:
            if n >= 12:
                m = int(math.floor(n / 12))
                out += str(m) + "Y"
                n %= 12
            if n != 0 or m == 0:
                return out + str(n) + "M"
            else:
                return out
        elif self.units == TimeUnits.Years:
            return out + str(n) + "Y"
        elif self.units == TimeUnits.BDays:
            return out + str(n) + "B"


# implementation detail


def _daysMinMax(p):
    if p.units == TimeUnits.Days:
        return p.length, p.length
    elif p.units == TimeUnits.Weeks:
        return 7 * p.length, 7 * p.length
    elif p.units == TimeUnits.Months:
        return 28 * p.length, 31 * p.length
    elif p.units == TimeUnits.Years:
        return 365 * p.length, 366 * p.length
    elif p.units == TimeUnits.BDays:
        raise ValueError("Business days unit has not min max days")
