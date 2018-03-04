# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""

cdef class Deque:

    cdef public size_t window
    cdef public bint is_full
    cdef public list con
    cdef public size_t start

    cdef double dump(self, double value, double default=*)
    cdef size_t size(self)
    cdef bint isFull(self)
