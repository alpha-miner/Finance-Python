# -*- coding: utf-8 -*-
u"""
Created on 2017-2-10

@author: cheng.li
"""

cdef class Period(object):

    cdef public int _length
    cdef public int _units

    cpdef Period normalize(self)
    cpdef int length(self)
    cpdef int units(self)