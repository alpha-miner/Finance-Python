# -*- coding: utf-8 -*-
#cython: embedsignature=True
u"""
Created on 2017-1-1

@author: cheng.li
"""

import copy
import numpy as np
cimport numpy as np
cimport cython


cdef class Deque:

    def __init__(self,
                 int window,
                 int is_full=0,
                 con=None,
                 int start=0):
        self.window = window
        self.is_full = is_full
        if con:
            self.con = copy.deepcopy(con)
        else:
            self.con = []
        self.start = start

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef dump(self, value):
        cdef int n = self.start
        cdef int window = self.window

        if self.is_full:
            popout = self.con[n]
            self.con[n] = value
            self.start = (n + 1) % window
            return popout
        else:

            self.con.append(value)
            if len(self.con) == window:
                self.is_full = 1

            if hasattr(value, '__len__'):
                return np.array([np.nan] * len(value))
            else:
                return np.nan

    cdef int size(self):
        return len(self.con)

    cdef int isFull(self):
        return self.is_full == 1

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
    def __getitem__(self, item):
        return self.con[(self.start + item) % self.window]

    def __deepcopy__(self, memo):
        return Deque(self.window,
                     self.is_full,
                     self.con,
                     self.start)

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
            'window': self.window,
            'is_full': self.is_full,
            'con': self.con,
            'start': self.start
        }
        return Deque, (0,), d

    def __setstate__(self, state):
        self.window = state['window']
        self.is_full = state['is_full']
        self.con = state['con']
        self.start = state['start']
