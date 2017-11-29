# -*- coding: utf-8 -*-
u"""
Created on 2017-2-11

@author: cheng.li
"""

cimport numpy as np

cdef class SeriesValues(object):

    cdef public dict name_mapping
    cdef public np.ndarray values
    cdef public np.ndarray name_array

    cpdef SeriesValues mask(self, flags)
    cpdef object index(self)
    cpdef SeriesValues rank(self)
    cpdef SeriesValues zscore(self)
    cpdef SeriesValues unit(self)

    cpdef double mean(self)
    cpdef double percentile(self, double per)
    cpdef double dot(self, SeriesValues right)
    cpdef SeriesValues res(self, SeriesValues right)
    cpdef dict to_dict(self)


cdef SeriesValues residue(SeriesValues left, SeriesValues right)
