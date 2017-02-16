# -*- coding: utf-8 -*-
u"""
Created on 2017-2-11

@author: cheng.li
"""

cimport numpy as np

cdef class SecurityValues(object):

    cdef public object name_mapping
    cdef public np.ndarray values
    cdef public np.ndarray name_array

    cpdef SecurityValues mask(self, flags)
    cpdef object index(self)
    cpdef SecurityValues rank(self)
    cpdef SecurityValues zscore(self)
    cpdef double mean(self)
    cpdef double dot(self, SecurityValues right)