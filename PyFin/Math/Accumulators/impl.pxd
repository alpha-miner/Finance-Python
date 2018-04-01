# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""

cdef class Deque:

    cdef size_t window
    cdef public bint is_full
    cdef double* con
    cdef public size_t start
    cdef public size_t count

    cdef double dump(self, double value, double default=*)
    cdef inline size_t size(self)
    cdef inline bint isFull(self)
    cdef void set_data(self, bytes data)


cpdef object rebuild(bytes data, size_t window, bint is_full, size_t start, size_t count)