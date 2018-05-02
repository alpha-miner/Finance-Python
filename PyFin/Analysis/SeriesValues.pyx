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
from numpy import maximum
from numpy import minimum
from scipy.stats import rankdata
from PyFin.Math.MathConstants cimport NAN


cdef groupby(groups):
    cdef np.ndarray[long long, ndim=1] order = groups.argsort()
    t = groups[order]
    cdef np.ndarray[long long, ndim=1] index_diff = np.where(np.diff(t))[0]
    return np.concatenate([index_diff, [len(groups)]]), order


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

        if data.dtype == np.object:
            self.values = data.astype(float)
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

    cpdef list index(self):
        return list(self.name_mapping.keys())

    def __contains__(self, key):
        return key in self.name_mapping

    def __len__(self):
        return self.values.__len__()

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef SeriesValues rank(self, SeriesValues groups=None):
        cdef np.ndarray[double, ndim=1] data
        cdef np.ndarray[long long, ndim=1] order
        cdef np.ndarray[long long, ndim=1] index_diff
        cdef long long diff_loc
        cdef long long start = 0
        cdef np.ndarray[long long, ndim=1] curr_idx

        if groups:
            data = self.values.copy()
            index_diff, order = groupby(groups.values)
            start = 0
            for diff_loc in index_diff:
                curr_idx = order[start:diff_loc + 1]
                data[curr_idx] = rankdata(self.values[curr_idx]).astype(float) - 1.
                start = diff_loc + 1
            data[np.isnan(self.values)] = NAN
        else:
            data = rankdata(self.values).astype(float) - 1.
            data[np.isnan(self.values)] = NAN
        return SeriesValues(data, self.name_mapping)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.cdivision(True)
    cpdef SeriesValues zscore(self, SeriesValues groups=None):
        cdef np.ndarray[double, ndim=1] data
        cdef np.ndarray[long long, ndim=1] order
        cdef np.ndarray[long long, ndim=1] index_diff
        cdef long long diff_loc
        cdef long long start = 0
        cdef np.ndarray[long long, ndim=1] curr_idx
        cdef np.ndarray[double, ndim=1] values = self.values
        cdef np.ndarray[double, ndim=1] curr_values

        if groups:
            data = values.copy()
            index_diff, order = groupby(groups.values)
            start = 0
            for diff_loc in index_diff:
                curr_idx = order[start:diff_loc + 1]
                curr_values = data[curr_idx]
                data[curr_idx] = (curr_values - nanmean(curr_values)) / nanstd(curr_values)
                start = diff_loc + 1
            data[np.isnan(values)] = NAN
        else:
            data = (values - nanmean(values)) / nanstd(values)
            data[np.isnan(values)] = NAN
        return SeriesValues(data, self.name_mapping)

    cpdef SeriesValues unit(self):
        cdef np.ndarray[double, ndim=1] data = self.values
        return SeriesValues(data / nansum(np.abs(data)), self.name_mapping)

    cpdef SeriesValues mean(self, SeriesValues groups=None):
        cdef np.ndarray[double, ndim=1] data
        cdef np.ndarray[long long, ndim=1] order
        cdef np.ndarray[long long, ndim=1] index_diff
        cdef long long diff_loc
        cdef long long start = 0
        cdef np.ndarray[long long, ndim=1] curr_idx
        cdef np.ndarray[double, ndim=1] values = self.values

        if groups:
            data = values.copy()
            index_diff, order = groupby(groups.values)
            start = 0
            for diff_loc in index_diff:
                curr_idx = order[start:diff_loc + 1]
                data[curr_idx] = nanmean(values[curr_idx])
                start = diff_loc + 1
            data[np.isnan(values)] = NAN
        else:
            data = np.ones_like(values) * nanmean(values)
            data[np.isnan(values)] = NAN
        return SeriesValues(data, self.name_mapping)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.cdivision(True)
    cpdef SeriesValues percentile(self, SeriesValues groups=None):
        cdef np.ndarray[double, ndim=1] data
        cdef np.ndarray[long long, ndim=1] order
        cdef np.ndarray[long long, ndim=1] index_diff
        cdef long long diff_loc
        cdef long long start = 0
        cdef np.ndarray[long long, ndim=1] curr_idx
        cdef np.ndarray[double, ndim=1] curr_values
        cdef int size

        if groups:
            data = self.values.copy()
            index_diff, order = groupby(groups.values)
            start = 0
            for diff_loc in index_diff:
                curr_idx = order[start:diff_loc + 1]
                curr_values = data[curr_idx]
                size = len(curr_values) - 1 if len(curr_values) > 1 else 1
                data[curr_idx] = (rankdata(curr_values).astype(float) - 1.) / float(size)
                start = diff_loc + 1
            data[np.isnan(self.values)] = NAN
        else:
            size = len(self.values) - 1 if len(self.values) > 1 else 1
            data = (rankdata(self.values).astype(float) - 1.) / float(size)
            data[np.isnan(self.values)] = NAN
        return SeriesValues(data, self.name_mapping)

    cpdef double dot(self, SeriesValues right):
        return np.dot(self.values, right.values)

    cpdef SeriesValues res(self, SeriesValues right):
        cdef np.ndarray[double, ndim=1] y = self.values
        cdef np.ndarray[double, ndim=1] x = right.values
        cdef y_bar = nanmean(y)
        cdef x_bar = nanmean(x)
        y -= y_bar
        x -= x_bar

        cdef double beta = nansum(x * y) / nansum(x * x)
        return SeriesValues(y - beta * x, self.name_mapping)

    cpdef dict to_dict(self):
        keys = self.name_mapping.keys()
        return {k: self.values[self.name_mapping[k]] for k in keys}

    def __repr__(self):
        return 'SeriesValues({0})'.format(self.__str__())

    def __str__(self):
        return self.to_dict().__str__()


cpdef SeriesValues s_maximum(SeriesValues left, SeriesValues right):
    cdef np.ndarray[double, ndim=1] x = left.values
    cdef np.ndarray[double, ndim=1] y = right.values
    return SeriesValues(maximum(x, y), left.name_mapping)


cpdef SeriesValues s_minimum(SeriesValues left, SeriesValues right):
    cdef np.ndarray[double, ndim=1] x = left.values
    cdef np.ndarray[double, ndim=1] y = right.values
    return SeriesValues(minimum(x, y), left.name_mapping)