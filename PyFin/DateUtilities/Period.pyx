# -*- coding: utf-8 -*-
u"""
Created on 2017-1-30

@author: cheng.li
"""

import re
cimport cython
from libc.math cimport floor
from PyFin.Enums._TimeUnits cimport TimeUnits
from PyFin.Utilities.Asserts cimport pyFinAssert
from PyFin.Utilities.Asserts cimport pyEnsureRaise


_unitPattern = re.compile('[BbDdMmWwYy]{1}')
_numberPattern = re.compile('[-+]*[0-9]+')

_unitsDict = {'d': TimeUnits.Days,
              'b': TimeUnits.BDays,
              'w': TimeUnits.Weeks,
              'm': TimeUnits.Months,
              'y': TimeUnits.Years}


cdef class Period(object):

    def __init__(self, str reprStr=None, int length=0, int units=0):

        cdef int n
        cdef str unitsStr

        if reprStr:
            unitsPos = _unitPattern.search(reprStr)
            numPos = _numberPattern.search(reprStr)
            unitsStr = reprStr[unitsPos.start():unitsPos.end()].lower()
            n = int(reprStr[numPos.start():numPos.end()])
            self._length = n
            self._units = int(_unitsDict[unitsStr])
        else:
            self._length = length
            self._units = units

    cpdef int length(self):
        return self._length

    cpdef int units(self):
        return self._units

    cpdef Period normalize(self):
        cdef int length = self.length()
        cdef int units = self.units()
        if length != 0:
            if units == TimeUnits.BDays or units == TimeUnits.Weeks or units == TimeUnits.Years:
                return Period(length=length, units=units)
            elif units == TimeUnits.Months:
                if length % 12 == 0:
                    length //= 12
                    units = TimeUnits.Years
                return Period(length=length, units=units)
            elif units == TimeUnits.Days:
                if length % 7 == 0:
                    length //= 7
                    units = TimeUnits.Weeks
                return Period(length=length, units=units)
            else:
                pyEnsureRaise(TypeError, "wrong period units type {0}".format(units))

    def __div__(self, int n):

        cdef int resunits = self.units()
        cdef int reslength = self.length()

        if reslength % n == 0:
            reslength /= n
        else:
            if resunits == TimeUnits.Years:
                reslength *= 12
                resunits = TimeUnits.Months
            elif resunits == TimeUnits.Weeks:
                reslength *= 7
                resunits = TimeUnits.Days

            pyFinAssert(reslength % n == 0, ValueError, "{0} cannot be divided by {1:d}".format(self, n))

            reslength //= n

        return Period(length=reslength, units=resunits)


    # only work for python 3
    def __truediv__(self, int n):

        cdef int resunits = self.units()
        cdef int reslength = self.length()

        if reslength % n == 0:
            reslength /= n
        else:
            if resunits == TimeUnits.Years:
                reslength *= 12
                resunits = TimeUnits.Months
            elif resunits == TimeUnits.Weeks:
                reslength *= 7
                resunits = TimeUnits.Days

            pyFinAssert(reslength % n == 0, ValueError, "{0} cannot be divided by {1:d}".format(self, n))

            reslength //= n

        return Period(length=reslength, units=resunits)

    def __add__(self, p2):

        cdef int reslength = self.length()
        cdef int resunits = self.units()
        cdef int p2length = p2.length()
        cdef int p2units = p2.units()

        if reslength == 0:
            return Period(length=p2length, units=p2units)
        elif resunits == p2units:
            reslength += p2length
            return Period(length=reslength, units=resunits)
        else:
            if resunits == TimeUnits.Years:
                if p2units == TimeUnits.Months:
                    resunits = TimeUnits.Months
                    reslength = reslength * 12 + p2length
                elif p2units == TimeUnits.Weeks or p2units == TimeUnits.Days or p2units == TimeUnits.BDays:
                    pyFinAssert(p2length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2units))
                return Period(length=reslength, units=resunits)
            elif resunits == TimeUnits.Months:
                if p2units == TimeUnits.Years:
                    reslength += 12 * p2length
                elif p2units == TimeUnits.Weeks or p2units == TimeUnits.Days or p2units == TimeUnits.BDays:
                    pyFinAssert(p2length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2units))
                return Period(length=reslength, units=resunits)
            elif resunits == TimeUnits.Weeks:
                if p2units == TimeUnits.Days:
                    resunits = TimeUnits.Days
                    reslength = reslength * 7 + p2length
                elif p2units == TimeUnits.Years or p2units == TimeUnits.Months or p2units == TimeUnits.BDays:
                    pyFinAssert(p2length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2units))
                return Period(length=reslength, units=resunits)
            elif resunits == TimeUnits.Days:
                if p2units == TimeUnits.Weeks:
                    reslength += 7 * p2length
                elif p2units == TimeUnits.Years or p2units == TimeUnits.Months or p2units == TimeUnits.BDays:
                    pyFinAssert(p2length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2units))
                return Period(length=reslength, units=resunits)
            elif resunits == TimeUnits.BDays:
                if p2units == TimeUnits.Years or p2units == TimeUnits.Months or p2units == TimeUnits.Weeks or p2units == TimeUnits.Days:
                    pyFinAssert(p2length == 0, ValueError, "impossible addition between {0} and {1}".format(self, p2))
                else:
                    raise ValueError("unknown time unit ({0:d})".format(p2units))
                return Period(length=reslength, units=resunits)

    def __neg__(self):
        return Period(length=-self.length(), units=self.units())

    def __sub__(self, p2):
        return self + (-p2)

    def __str__(self):
        cdef str out = ""
        cdef int n = self.length()
        cdef int m = 0
        cdef int units = self.units()

        if units == TimeUnits.Days:
            if n >= 7:
                m = int(floor(n / 7,))
                out = '{0}W'.format(m)
                n %= 7
            if n != 0 or m == 0:
                return '{0}{1}D'.format(out, n)
            else:
                return out
        elif units == TimeUnits.Weeks:
            return '{0}W'.format(n)
        elif units == TimeUnits.Months:
            if n >= 12:
                m = int(floor(n / 12.))
                out = '{0}Y'.format(m)
                n %= 12
            if n != 0 or m == 0:
                return '{0}{1}M'.format(out, n)
            else:
                return out
        elif units == TimeUnits.Years:
            return '{0}Y'.format(n)
        elif units == TimeUnits.BDays:
            return '{0}B'.format(n)

    def __richcmp__(self, right, int op):
        if op == 0:
            return _lt_cmp(self, right)
        elif op == 2:
            return not (_lt_cmp(self, right) or _lt_cmp(right, self))
        elif op == 3:
            return _lt_cmp(self, right) or _lt_cmp(right, self)
        elif op == 4:
            return _lt_cmp(right, self)

    def __deepcopy__(self, memo):
        return Period(length=self.length(), units=self.units())

    def __reduce__(self):
        d = {}

        return Period, (None, self.length(), self.units()), d

    def __setstate__(self, state):
        pass


cpdef check_period(p):
    if isinstance(p, Period):
        return p
    else:
        return Period(p)


# implementation detail

cdef bint _lt_cmp(Period p1, Period p2) except -1:

    cdef tuple p1lim
    cdef tuple p2lim
    cdef int p1length = p1.length()
    cdef int p1units = p1.units()
    cdef int p2length = p2.length()
    cdef int p2units = p2.units()

    if p1length == 0:
        return p2length > 0

    if p2length == 0:
        return p1length < 0

    # exact comparisons
    if p1units == p2units:
        return p1length < p2length
    elif p1units == TimeUnits.Months and p2units == TimeUnits.Years:
        return p1length < (p2length * 12)
    elif p1units == TimeUnits.Years and p2units == TimeUnits.Months:
        return (p1length * 12) < p2length
    elif p1units == TimeUnits.Days and p2units == TimeUnits.Weeks:
        return p1length < (p2length * 7)
    elif p1units == TimeUnits.Weeks and p2units == TimeUnits.Days:
        return (p1length * 7) < p2length

    # inexact comparisons (handled by converting to days and using limits)

    p1lim = _daysMinMax(p1)
    p2lim = _daysMinMax(p2)

    if p1lim[1] < p2lim[0]:
        return True
    elif p1lim[0] >= p2lim[1]:
        return False
    else:
        pyEnsureRaise(ValueError, "undecidable comparison between {0} and {1}".format(p1, p2))


cdef tuple _daysMinMax(Period p):

    cdef int units = p.units()
    cdef int length = p.length()

    if units == TimeUnits.Days:
        return length, length
    elif units == TimeUnits.Weeks:
        return 7 * length, 7 * length
    elif units == TimeUnits.Months:
        return 28 * length, 31 * length
    elif units == TimeUnits.Years:
        return 365 * length, 366 * length
    elif units == TimeUnits.BDays:
        pyEnsureRaise(ValueError, "Business days unit has not min max days")