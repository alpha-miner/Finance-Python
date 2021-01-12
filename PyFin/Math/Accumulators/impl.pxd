# -*- coding: utf-8 -*-
# distutils: language = c++
u"""
Created on 2017-2-8

@author: cheng.li
"""

from libcpp.list cimport list as CList

cdef class Deque:

    cdef size_t window
    cdef public bint is_full
    cdef double* con
    cdef public size_t start
    cdef public size_t count

    cdef double dump(self, double value, double default=*)
    cpdef list dumps(self, values)
    cdef inline size_t size(self)
    cdef inline bint isFull(self)
    cpdef size_t idx(self, double value)
    cpdef double sum(self)
    cdef void set_data(self, bytes data)

cpdef object rebuild(bytes data, size_t window, bint is_full, size_t start, size_t count)

cdef class DiffDeque:

    cdef double window
    cdef public bint is_full
    cdef CList[double] con
    cdef CList[double] stamps

    cdef CList[double] dump(self, double value, int stamp, double default= *)
    cpdef CList[double] dumps(self, values, stamps)
    cpdef size_t size(self)
    cpdef bint isFull(self)
    cpdef size_t idx(self, double value)
    cpdef double sum(self)

cpdef object rebuild2(double window)