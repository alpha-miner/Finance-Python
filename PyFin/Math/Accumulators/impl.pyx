# -*- coding: utf-8 -*-
u"""
Created on 2017-1-1

@author: cheng.li
"""

import copy
import numpy as np
cimport numpy as np

cdef class Deque:

    cdef int window
    cdef int is_full
    cdef list con
    cdef int start

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

    cpdef dump(self, value):
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

    cpdef size(self):
        return len(self.con)

    cpdef isFull(self):
        return self.is_full == 1

    cpdef as_array(self):
        return np.array(self.as_list())

    cpdef as_list(self):
        return [self.con[(self.start + item) % self.window] for item in range(len(self.con))]

    def __getitem__(self, item):
        return self.con[(self.start + item) % self.window]

    def __deepcopy__(self, memo):
        return Deque(self.window,
                     self.is_full,
                     self.con,
                     self.start)