# -*- coding: utf-8 -*-
u"""
Created on 2017-2-10

@author: cheng.li
"""

cdef class Date(object):

    cdef public int __serialNumber__
    cdef public int _year
    cdef public int _month
    cdef public int _day

    cpdef int dayOfMonth(self)

    cpdef int dayOfYear(self)

    cpdef int year(self)

    cpdef int month(self)

    cpdef int weekday(self)

    cpdef toDateTime(self)

    cdef _calculate_date(self, int year, int month, int day)


cpdef check_date(date)