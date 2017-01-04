# -*- coding: utf-8 -*-
u"""
Created on 2017-1-1

@author: cheng.li
"""

import copy
import numpy as np
cimport numpy as np
import cython


cdef class Deque:

    cdef public int window
    cdef public int is_full
    cdef public list con
    cdef public int start

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

    @cython.boundscheck(False)
    def dump(self, value):
        cdef int n
        n = self.start

        if self.is_full:
            popout = self.con[n]
            self.con[n] = value
            self.start = (n + 1) % self.window
        else:
            if hasattr(value, '__len__'):
                popout = np.array([np.nan] * len(value))
            else:
                popout = np.nan

            self.con.append(value)
            if len(self.con) == self.window:
                self.is_full = 1
        return popout

    def size(self):
        return len(self.con)

    def isFull(self):
        return self.is_full == 1

    def as_array(self):
        return np.array(self.as_list())

    def as_list(self):
        return [self.con[(self.start + item) % self.window] for item in range(len(self.con))]

    def __getitem__(self, item):
        return self.con[(self.start + item) % self.window]

    def __deepcopy__(self, memo):
        return Deque(self.window,
                     self.is_full,
                     self.con,
                     self.start)

    def __getstate__(self):
        return (self.window,
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

    def __setstate__(self, state):
        window, is_full, con, start = state
        self.window = window
        self.is_full = is_full
        self.con = con
        self.start = start
