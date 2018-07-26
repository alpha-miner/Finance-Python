# -*- coding: utf-8 -*-

cdef class InverseCumulativeNormal(object):

    cdef double _average
    cdef double _sigma
    cdef int _fullAcc

    cdef double _standard_value(self, double x)
    cdef double inv(self, double x)
