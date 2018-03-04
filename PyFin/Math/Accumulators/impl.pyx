# -*- coding: utf-8 -*-
u"""
Created on 2017-1-1

@author: cheng.li
"""

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
    cdef double dump(self, double value, double default=NAN):
        cdef size_t n = self.start
        cdef list con = self.con
        cdef double popout

        if self.is_full:
            popout = con[n]
            con[n] = value
            self.start = (n + 1) % self.window
            return popout
        else:
            con.append(value)
            self.is_full = len(con) == self.window
            return default

    cdef size_t size(self):
        return len(self.con)

    cdef bint isFull(self):
        return self.is_full

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    def __getitem__(self, size_t item):
        return self.con[(self.start + item) % self.window]

    def __richcmp__(Deque self, Deque other, int op):
        cdef bint flag = False
        if op == 2:
            flag = self.window == other.window \
                   and self.is_full == other.is_full \
                   and self.start == other.start \
                   and self.con == other.con

        elif op == 3:
            return not self.__richcmp__(other, 2)