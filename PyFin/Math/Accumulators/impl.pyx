# -*- coding: utf-8 -*-
u"""
Created on 2017-1-1

@author: cheng.li
"""

import copy
import numpy as np
cimport numpy as np
cimport cython
from PyFin.Math.MathConstants cimport NAN


cdef class Deque:

    def __init__(self,
                 size_t window):
        self.window = window
        self.is_full = False
        self.con = []
        self.start = 0

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef dump(self, value, default=NAN):
        cdef size_t n = self.start
        cdef size_t window = self.window
        cdef list con = self.con

        if self.is_full:
            popout = con[n]
            con[n] = value
            self.start = (n + 1) % window
            return popout
        else:
            con.append(value)
            self.is_full = len(con) == window
            return default

    cdef size_t size(self):
        return len(self.con)

    cdef bint isFull(self):
        return self.is_full

    cdef np.ndarray as_array(self):
        return np.array(self.as_list())

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef list as_list(self):
        return [self.con[(self.start + item) % self.window] for item in range(len(self.con))]

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    def __getitem__(self, size_t item):
        return self.con[(self.start + item) % self.window]

    def __deepcopy__(self, memo):
        copied = Deque(self.window)
        copied.is_full = self.is_full
        copied.con = copy.deepcopy(self.con)
        copied.start = self.start
        return copied

    def __richcmp__(Deque self, Deque other, int op):
        if op == 2:
            return self.window == other.window \
                   and self.is_full == other.is_full \
                   and self.con == other.con \
                   and self.start == other.start
        elif op == 3:
            return self.window != other.window \
                   or self.is_full != other.is_full \
                   or self.con != other.con \
                   or self.start != other.start

    def __reduce__(self):
        d = {
            'is_full': self.is_full,
            'con': self.con,
            'start': self.start
            }
        return Deque, (self.window,), d

    def __setstate__(self, state):
        self.is_full = state['is_full']
        self.con = state['con']
        self.start = state['start']
