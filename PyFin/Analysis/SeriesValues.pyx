# -*- coding: utf-8 -*-
u"""
Created on 2017-2-7

@author: cheng.li
"""

cimport cython
import numpy as np
cimport numpy as np
from numpy import nansum
from numpy import nanmean
from numpy import nanstd
from numpy import percentile
from PyFin.Math.MathConstants cimport NAN


@cython.cdivision(True)
cdef SeriesValues residue(SeriesValues left, SeriesValues right):
    cdef np.ndarray[double, ndim=1] y = left.values
    cdef np.ndarray[double, ndim=1] x = right.values

    cdef double beta = nansum(x * y) / nansum(x * x)
    return SeriesValues(y - beta * x, left.name_mapping)


cdef class SeriesValues(object):

    def __init__(self, data, index=None):
        if isinstance(data, dict):
            keys = sorted(data.keys())
            index = dict(zip(keys, range(len(data))))
            data = np.array([data[k] for k in keys])

        if data.dtype == np.object and len(data) > 0:
            if isinstance(data[0], float) or isinstance(data[0], int):
                self.values = data.astype(float)
            else:
                self.values = data
        else:
            self.values = data

        if isinstance(index, dict):
            self.name_mapping = index
        else:
            self.name_mapping = dict(zip(index, range(len(index))))
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
            data = np.array([values[name_mapping[n]] if n in name_mapping else NAN for n in name])
            return SeriesValues(data, dict(zip(name, range(len(name)))))

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef SeriesValues mask(self, flags):
        if not self.name_array:
            self.name_array = np.array(sorted(self.name_mapping.keys()), dtype=str)

        filtered_names = self.name_array[flags]
        return SeriesValues(self.values[flags], dict(zip(filtered_names, range(len(filtered_names)))))

    def __invert__(self):
        return SeriesValues(~self.values, self.name_mapping)

    def __neg__(self):
        return SeriesValues(-self.values, self.name_mapping)

    def __add__(self, right):
        if isinstance(right, SeriesValues):
            if isinstance(self, SeriesValues):
                return SeriesValues(self.values + right.values, self.name_mapping)
            else:
                return SeriesValues(self + right.values, right.name_mapping)
        else:
            return SeriesValues(self.values + right, self.name_mapping)

    def __sub__(self, right):
        if isinstance(right, SeriesValues):
            if isinstance(self, SeriesValues):
                return SeriesValues(self.values - right.values, self.name_mapping)
            else:
                return SeriesValues(self - right.values, right.name_mapping)
        else:
            return SeriesValues(self.values - right, self.name_mapping)

    def __mul__(self, right):
        if isinstance(right, SeriesValues):
            if isinstance(self, SeriesValues):
                return SeriesValues(self.values * right.values, self.name_mapping)
            else:
                return SeriesValues(self * right.values, right.name_mapping)
        else:
            return SeriesValues(self.values * right, self.name_mapping)

    @cython.cdivision(True)
    def __truediv__(self, right):
        cdef np.ndarray[double, ndim=1] values
        cdef dict name_mapping
        if isinstance(right, SeriesValues):
            if isinstance(self, SeriesValues):
                values = self.values / right.values
                name_mapping = self.name_mapping
            else:
                values = self / right.values
                name_mapping = right.name_mapping
        else:
            values = self.values / right
            name_mapping = self.name_mapping

        values[~np.isfinite(values)] = NAN
        return SeriesValues(values, name_mapping)

    @cython.cdivision(True)
    def __div__(self, right):
        cdef np.ndarray[double, ndim=1] values
        cdef dict name_mapping
        if isinstance(right, SeriesValues):
            if isinstance(self, SeriesValues):
                values = self.values / right.values
                name_mapping = self.name_mapping
            else:
                values = self / right.values
                name_mapping = right.name_mapping
        else:
            values = self.values / right
            name_mapping = self.name_mapping

        values[~np.isfinite(values)] = NAN
        return SeriesValues(values, name_mapping)

    def __and__(self, right):
        if isinstance(right, SeriesValues):
            if isinstance(self, SeriesValues):
                return SeriesValues(self.values & right.values, self.name_mapping)
            else:
                return SeriesValues(self & right.values, right.name_mapping)
        else:
            return SeriesValues(self.values & right, self.name_mapping)

    def __or__(self, right):
        if isinstance(right, SeriesValues):
            if isinstance(self, SeriesValues):
                return SeriesValues(self.values | right.values, self.name_mapping)
            else:
                return SeriesValues(self | right.values, right.name_mapping)
        else:
            return SeriesValues(self.values | right, self.name_mapping)

    def __xor__(self, right):
        if isinstance(right, SeriesValues):
            if isinstance(self, SeriesValues):
                return SeriesValues(np.array([self.values, right.values]).T, self.name_mapping)
            else:
                return SeriesValues(np.array([np.ones(len(right.values)) * self, right.values]).T, self.name_mapping)
        else:
            return SeriesValues(np.array([self.values, np.ones(len(self.values)) * right]).T, self.name_mapping)

    def __richcmp__(self, right, int op):

        if isinstance(right, SeriesValues):
            if op == 0:
                return SeriesValues(self.values < right.values, self.name_mapping)
            elif op == 1:
                return SeriesValues(self.values <= right.values, self.name_mapping)
            elif op == 2:
                return SeriesValues(self.values == right.values, self.name_mapping)
            elif op == 3:
                return SeriesValues(self.values != right.values, self.name_mapping)
            elif op == 4:
                return SeriesValues(self.values > right.values, self.name_mapping)
            elif op == 5:
                return SeriesValues(self.values >= right.values, self.name_mapping)
        else:
            if op == 0:
                return SeriesValues(self.values < right, self.name_mapping)
            elif op == 1:
                return SeriesValues(self.values <= right, self.name_mapping)
            elif op == 2:
                return SeriesValues(self.values == right, self.name_mapping)
            elif op == 3:
                return SeriesValues(self.values != right, self.name_mapping)
            elif op == 4:
                return SeriesValues(self.values > right, self.name_mapping)
            elif op == 5:
                return SeriesValues(self.values >= right, self.name_mapping)

    cpdef object index(self):
        return self.name_mapping.keys()

    def __contains__(self, key):
        return key in self.name_mapping

    def __len__(self):
        return self.values.__len__()

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef SeriesValues rank(self):
        cdef np.ndarray[double, ndim=1] data = self.values.argsort().argsort().astype(float)
        data[np.isnan(self.values)] = NAN
        return SeriesValues(data + 1., self.name_mapping)

    cpdef SeriesValues zscore(self):
        cdef np.ndarray[double, ndim=1] data = self.values
        return SeriesValues((data - nanmean(data)) / nanstd(data), self.name_mapping)

    cpdef SeriesValues unit(self):
        cdef np.ndarray[double, ndim=1] data = self.values
        return SeriesValues(data / nansum(np.abs(data)), self.name_mapping)

    cpdef double mean(self):
        return nanmean(self.values)

    cpdef double percentile(self, double per):
        return percentile(self.values, per)

    cpdef double dot(self, SeriesValues right):
        return np.dot(self.values, right.values)


    cpdef SeriesValues res(self, SeriesValues right):
        return residue(self, right)

    cpdef dict to_dict(self):
        keys = self.name_mapping.keys()
        return {k: self.values[self.name_mapping[k]] for k in keys}

    def __repr__(self):
        return 'SeriesValues({0})'.format(self.__str__())

    def __str__(self):
        return self.to_dict().__str__()


