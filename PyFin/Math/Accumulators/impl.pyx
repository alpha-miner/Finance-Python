# -*- coding: utf-8 -*-
# distutils: language = c++
u"""
Created on 2017-1-1

@author: cheng.li
"""

cimport cython
from PyFin.Math.MathConstants cimport NAN
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from libc.math cimport isnan
from libc.string cimport memcpy
from libcpp.list cimport list as CList
from libcpp.string cimport string as CString
from cython.operator import dereference, preincrement
from PyFin.Utilities.Asserts cimport pyFinAssert


cdef class Deque:

    def __cinit__(self,
                  size_t window):
        self.window = window
        self.is_full = False
        self.con = <double*> PyMem_Malloc(window * sizeof(double))
        for i in range(window):
            self.con[i] = 0.
        self.start = 0
        self.count = 0

    def __dealloc__(self):
        PyMem_Free(self.con)

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef double dump(self, double value, double default=NAN):
        cdef size_t n = self.start
        cdef double* con = self.con
        cdef double popout

        if self.is_full:
            popout = con[n]
            con[n] = value
            self.start = (n + 1) % self.window
            return popout
        else:
            con[self.count] = value
            self.count += 1
            self.is_full = self.count == self.window
            return default

    cpdef list dumps(self, values):
        cdef ret_values = []
        for v in values:
            ret_values.append(self.dump(v))
        return ret_values

    cdef inline size_t size(self):
        return self.count

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef size_t idx(self, double value):
        cdef size_t i
        for i in range(self.count):
            if value == self.con[i]:
                break
        else:
            i = -1
        if i < 0:
            return -1
        else:
            i = (i - self.start + self.window) % self.window
        return i

    cdef inline bint isFull(self):
        return self.is_full

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef double sum(self):
        cdef double x = self.con[0]
        cdef int i
        for i in range(1, self.count):
            x += self.con[i]
        return x

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    def __getitem__(self, size_t item):
        return self.con[(self.start + item) % self.window]

    def __richcmp__(Deque self, Deque other, int op):
        cdef bint flag = False
        cdef int i
        if op == 2:
           flag =  self.window == other.window \
                   and self.is_full == other.is_full \
                   and self.start == other.start

           if flag:
               for i in range(self.window):
                   if self.con[i] != other.con[i]:
                       return False
               return True
           else:
               return False

        elif op == 3:
            return not self.__richcmp__(other, 2)

    cdef void set_data(self, bytes data):
        memcpy(self.con, <char*>data, sizeof(double)*self.window)

    def __reduce__(self):
        cdef bytes data = <bytes>(<char *>self.con)[:sizeof(double)*self.window]
        return rebuild, (data, self.window, self.is_full, self.start, self.count)


cpdef object rebuild(bytes data, size_t window, bint is_full, size_t start, size_t count):
    c = Deque(window)
    c.set_data(data)
    c.is_full = is_full
    c.start = start
    c.count = count
    return c


cdef CString _RIGHT = "right".encode("UTF-8")
cdef CString _LEFT = "left".encode("UTF-8")
cdef CString _BOTH = "both".encode("UTF-8")
cdef CString _NEITHER = "neither".encode("UTF-8")


cdef class DiffDeque:

    def __cinit__(self,
                  window,
                  closed="right"):
        self.window = window
        self.con = CList[double]()
        self.stamps = CList[double]()
        cdef str closed_str = closed.lower()
        pyFinAssert(closed_str in ("left", "right", "both", "neither"),
                    ValueError,
                    "closed parameter is <{0}> which is not in the recognized formats".format(closed))
        self.closed = closed_str.encode("UTF-8")
        self.last = NAN
        self.last_stamp = NAN

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef CList[double] dump(self, double value, int stamp, double default=NAN):
        cdef CList[double] ret_values = CList[double]()
        if self.closed == _BOTH or self.closed == _LEFT:
            while self.con.size() > 0 and (stamp - self.stamps.front()) > self.window:
                ret_values.push_back(self.con.front())
                self.con.pop_front()
                self.stamps.pop_front()
        else:
            while self.con.size() > 0 and (stamp - self.stamps.front()) >= self.window:
                ret_values.push_back(self.con.front())
                self.con.pop_front()
                self.stamps.pop_front()
        if self.closed == _RIGHT or self.closed == _BOTH:
            self.con.push_back(value)
            self.stamps.push_back(stamp)
        else:
            if not isnan(self.last):
                if (self.closed == _NEITHER and (stamp - self.last_stamp) < self.window) \
                    or (self.closed == _LEFT and (stamp - self.last_stamp) <= self.window):
                    self.con.push_back(self.last)
                    self.stamps.push_back(self.last_stamp)
        self.last = value
        self.last_stamp = stamp
        return ret_values

    cpdef CList[double] dumps(self, values, stamps):
        cdef CList[double] ret_values = CList[double]()
        cdef CList[double] tmp
        for v, s in zip(values, stamps):
            tmp = self.dump(v, s)
            ret_values.merge(tmp)
        return ret_values

    cpdef size_t size(self):
        return self.size()

    cpdef bint isFull(self):
        if self.con.size() > 0:
            return True
        else:
            return False

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef size_t idx(self, double value):
        cdef size_t i
        cdef CList[double].iterator it
        it = self.con.begin()
        for i in range(self.con.size()):
            if value == dereference(it):
                break
            else:
                preincrement(it)
        else:
            i = -1
        return i

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef double sum(self):
        cdef double x = 0.0
        cdef size_t i
        cdef CList[double].iterator it
        it = self.con.begin()
        for i in range(self.con.size()):
            x += dereference(it)
            preincrement(it)
        return x

    cpdef CString close(self):
        return self.closed

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    def __getitem__(self, size_t item):
        cdef size_t i
        cdef CList[double].iterator it
        it = self.con.begin()
        for i in range(self.con.size()):
            if i == item:
                return dereference(it)
            preincrement(it)

    def __richcmp__(Deque self, DiffDeque other, int op):
        cdef bint flag = False
        cdef int i
        if op == 2:
            flag = self.window == other.window \
                   and self.is_full == other.is_full
            if flag:
                return True
            else:
                return False

        elif op == 3:
            return not self.__richcmp__(other, 2)

    def __reduce__(self):
        return rebuild2, (self.window, self.closed.decode("UTF-8"))

cpdef object rebuild2(double window, str closed):
    c = DiffDeque(window, closed)
    return c
