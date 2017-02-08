# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""

cdef class Deque:

    cdef public int window
    cdef public int is_full
    cdef public list con
    cdef public int start

    cdef dump(self, value)
    cdef size(self)
    cdef isFull(self)
    cdef as_array(self)
    cdef as_list(self)