# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""

cimport numpy as np

cdef class Deque:

    cdef public size_t window
    cdef public bint is_full
    cdef public list con
    cdef public size_t start

    cdef dump(self, value)
    cdef size_t size(self)
    cdef bint isFull(self)
    cdef np.ndarray as_array(self)
    cdef list as_list(self)
