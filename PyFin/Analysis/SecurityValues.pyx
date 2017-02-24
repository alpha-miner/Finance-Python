# -*- coding: utf-8 -*-
u"""
Created on 2017-2-7

@author: cheng.li
"""

from collections import OrderedDict
cimport cython
import numpy as np
cimport numpy as np


cdef class SecurityValues(object):

    def __init__(self, data, index=None):
        if isinstance(data, dict):
            keys = sorted(data.keys())
            index = OrderedDict(zip(keys, range(len(data))))
            data = np.array([data[k] for k in keys])

        if data.dtype == np.object and len(data) > 0:
            if isinstance(data[0], float) or isinstance(data[0], int):
                self.values = data.astype(float)
            else:
                self.values = data
        else:
            self.values = data

        if isinstance(index, OrderedDict):
            self.name_mapping = index
        else:
            self.name_mapping = OrderedDict(zip(index, range(len(index))))
        self.name_array = None

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def __getitem__(self, name):

        cdef np.ndarray data
        cdef np.ndarray values

        if not isinstance(name, list):
            return self.values[self.name_mapping[name]]
        else:

            values = self.values
            name_mapping = self.name_mapping
            data = np.array([values[name_mapping[n]] if n in name_mapping else np.nan for n in name])
            return SecurityValues(data, OrderedDict(zip(name, range(len(name)))))

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef SecurityValues mask(self, flags):
        if not self.name_array:
            self.name_array = np.array(list(self.name_mapping.keys()))

        filtered_names = self.name_array[flags]
        return SecurityValues(self.values[flags], OrderedDict(zip(filtered_names, range(len(filtered_names)))))

    def __invert__(self):
        return SecurityValues(~self.values, self.name_mapping)

    def __neg__(self):
        return SecurityValues(-self.values, self.name_mapping)

    def __add__(self, right):
        if isinstance(right, SecurityValues):
            if isinstance(self, SecurityValues):
                return SecurityValues(self.values + right.values, self.name_mapping)
            else:
                return SecurityValues(self + right.values, right.name_mapping)
        else:
            return SecurityValues(self.values + right, self.name_mapping)

    def __sub__(self, right):
        if isinstance(right, SecurityValues):
            if isinstance(self, SecurityValues):
                return SecurityValues(self.values - right.values, self.name_mapping)
            else:
                return SecurityValues(self - right.values, right.name_mapping)
        else:
            return SecurityValues(self.values - right, self.name_mapping)

    def __mul__(self, right):
        if isinstance(right, SecurityValues):
            if isinstance(self, SecurityValues):
                return SecurityValues(self.values * right.values, self.name_mapping)
            else:
                return SecurityValues(self * right.values, right.name_mapping)
        else:
            return SecurityValues(self.values * right, self.name_mapping)

    @cython.cdivision(True)
    def __truediv__(self, right):
        if isinstance(right, SecurityValues):
            if isinstance(self, SecurityValues):
                return SecurityValues(self.values / right.values, self.name_mapping)
            else:
                return SecurityValues(self / right.values, right.name_mapping)
        else:
            return SecurityValues(self.values / right, self.name_mapping)

    @cython.cdivision(True)
    def __div__(self, right):
        if isinstance(right, SecurityValues):
            if isinstance(self, SecurityValues):
                return SecurityValues(self.values / right.values, self.name_mapping)
            else:
                return SecurityValues(self / right.values, right.name_mapping)
        else:
            return SecurityValues(self.values / right, self.name_mapping)

    def __and__(self, right):
        if isinstance(right, SecurityValues):
            if isinstance(self, SecurityValues):
                return SecurityValues(self.values & right.values, self.name_mapping)
            else:
                return SecurityValues(self & right.values, right.name_mapping)
        else:
            return SecurityValues(self.values & right, self.name_mapping)

    def __or__(self, right):
        if isinstance(right, SecurityValues):
            if isinstance(self, SecurityValues):
                return SecurityValues(self.values | right.values, self.name_mapping)
            else:
                return SecurityValues(self | right.values, right.name_mapping)
        else:
            return SecurityValues(self.values | right, self.name_mapping)

    def __richcmp__(self, right, int op):

        if isinstance(right, SecurityValues):
            if op == 0:
                return SecurityValues(self.values < right.values, self.name_mapping)
            elif op == 1:
                return SecurityValues(self.values <= right.values, self.name_mapping)
            elif op == 2:
                return SecurityValues(self.values == right.values, self.name_mapping)
            elif op == 3:
                return SecurityValues(self.values != right.values, self.name_mapping)
            elif op == 4:
                return SecurityValues(self.values > right.values, self.name_mapping)
            elif op == 5:
                return SecurityValues(self.values >= right.values, self.name_mapping)
        else:
            if op == 0:
                return SecurityValues(self.values < right, self.name_mapping)
            elif op == 1:
                return SecurityValues(self.values <= right, self.name_mapping)
            elif op == 2:
                return SecurityValues(self.values == right, self.name_mapping)
            elif op == 3:
                return SecurityValues(self.values != right, self.name_mapping)
            elif op == 4:
                return SecurityValues(self.values > right, self.name_mapping)
            elif op == 5:
                return SecurityValues(self.values >= right, self.name_mapping)

    cpdef object index(self):
        return self.name_mapping.keys()

    def __contains__(self, key):
        return key in self.name_mapping

    def __len__(self):
        return self.values.__len__()

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef SecurityValues rank(self):
        cdef np.ndarray[double, ndim=1] data = self.values.argsort().argsort().astype(float)
        data[np.isnan(self.values)] = np.nan
        return SecurityValues(data + 1., self.name_mapping)

    cpdef SecurityValues zscore(self):
        cdef np.ndarray[double, ndim=1] data = self.values
        return SecurityValues((data - data.mean()) / data.std(), self.name_mapping)

    cpdef double mean(self):
        return np.nanmean(self.values)

    cpdef double dot(self, SecurityValues right):
        return np.dot(self.values, right.values)

    def __deepcopy__(self, memo):
        return SecurityValues(self.values, self.name_mapping)

    def __reduce__(self):
        d = {}
        return SecurityValues, (self.values, self.name_mapping), d

    def __setstate__(self, state):
        pass

    def __str__(self):
        return dict(zip(self.values, self.name_mapping.keys())).__str__()
