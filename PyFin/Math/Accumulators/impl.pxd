# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""

cimport numpy as np

cdef class Deque:

    cdef public int window
    cdef public int is_full
    cdef public list con
    cdef public int start

    cdef dump(self, value)
    cdef int size(self)
    cdef int isFull(self)
    cdef np.ndarray as_array(self)
    cdef list as_list(self)
