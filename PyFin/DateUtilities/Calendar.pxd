# -*- coding: utf-8 -*-
u"""
Created on 2015-2-20

@author: cheng.li
"""

from PyFin.DateUtilities.Date cimport Date
from PyFin.DateUtilities.Period cimport Period


cdef class CalendarImpl(object):

    cdef bint isBizDay(self, Date date)
    cdef bint isWeekEnd(self, int weekDay)


cdef class Calendar(object):

    cdef public CalendarImpl _impl
    cdef public str name

    cpdef isBizDay(self, Date d)
    cpdef isHoliday(self, Date d)
    cpdef isWeekEnd(self, int weekday)
    cpdef isEndOfMonth(self, Date d)
    cpdef endOfMonth(self, Date d)
    cpdef bizDaysBetween(self, Date fromDate, Date toDate, bint includeFirst=*, bint includeLast=*)
    cpdef adjustDate(self, Date d, int c=*)
    cpdef advanceDate(self, Date d, Period period, int c=*, bint endOfMonth=*)
    cpdef holDatesList(self, Date fromDate, Date toDate, bint includeWeekEnds=*)
    cpdef bizDatesList(self, Date fromDate, Date toDate)