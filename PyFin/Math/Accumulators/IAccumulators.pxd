# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""


cdef class IAccumulator(object):
    pass


cdef class Accumulator(IAccumulator):

    cdef public int _isFull
    cdef public object _dependency
    cdef public int _isValueHolderContained
    cdef public int _window
    cdef public int _returnSize

    cdef extract(self, dict data)


cdef class StatelessSingleValueAccumulator(Accumulator):

    cdef _push(self, dict data)