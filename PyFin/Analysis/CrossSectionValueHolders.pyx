# -*- coding: utf-8 -*-
u"""
Created on 2017-2-10

@author: cheng.li
"""

import copy
import six
import numpy as np
cimport numpy as np
cimport cython
from PyFin.Analysis.SeriesValues cimport SeriesValues
from PyFin.Analysis.SecurityValueHolders cimport SecurityValueHolder
from PyFin.Analysis.SecurityValueHolders import build_holder
from PyFin.Math.MathConstants cimport NAN


cdef class CrossSectionValueHolder(SecurityValueHolder):

    cdef SecurityValueHolder _inner
    cdef SecurityValueHolder _group

    def __init__(self, innerValue, groups=None):
        super(CrossSectionValueHolder, self).__init__()
        self._inner = build_holder(innerValue)
        self._group = build_holder(groups) if groups else None
        if self._group:
            self._window = max(self._inner.window, self._group.window)
            self._dependency = list(set(self._inner.fields + self._group.fields))
        else:
            self._window = self._inner.window
            self._dependency = copy.deepcopy(self._inner.fields)
        self.updated = 0
        self.cached = None

    @property
    def symbolList(self):
        return self._inner.symbolList

    cpdef push(self, dict data):
        self._inner.push(data)
        if self._group:
            self._group.push(data)
        self.updated = 0


cdef class CSRankedSecurityValueHolder(CrossSectionValueHolder):

    def __init__(self, innerValue, groups=None):
        super(CSRankedSecurityValueHolder, self).__init__(innerValue, groups)

    cdef _cal_impl(self):
        cdef SeriesValues raw_values = self._inner.value

        if self._group:
            self.cached = raw_values.rank(self._group.value)
        else:
            self.cached = raw_values.rank()
        self.updated = 1

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            self._cal_impl()
            return self.cached

    cpdef double value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            self._cal_impl()
            return self.cached[name]

    cpdef SeriesValues value_by_names(self, list names):
        cdef SeriesValues raw_values = self._inner.value_by_names(names)
        if self._group:
            raw_values = raw_values.rank(self._group.value_by_names(names))
        else:
            raw_values = raw_values.rank()
        return raw_values

    def __str__(self):
        if self._group:
            return "\mathrm{{CSRank}}({0}, groups={1})".format(str(self._inner), str(self._group))
        else:
            return "\mathrm{{CSRank}}({0})".format(str(self._inner))


cdef class CSAverageSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue, groups=None):
        super(CSAverageSecurityValueHolder, self).__init__(innerValue, groups)

    cdef _cal_impl(self):
        cdef SeriesValues raw_values = self._inner.value

        if self._group:
            self.cached = raw_values.mean(self._group.value)
        else:
            self.cached = raw_values.mean()
        self.updated = 1

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            self._cal_impl()
            return self.cached

    cpdef double value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            self._cal_impl()
            return self.cached[name]

    cpdef SeriesValues value_by_names(self, list names):
        cdef SeriesValues raw_values = self._inner.value_by_names(names)
        if self._group:
            raw_values = raw_values.mean(self._group.value_by_names(names))
        else:
            raw_values = raw_values.mean()
        return raw_values

    def __str__(self):
        if self._group:
            return "\mathrm{{CSMean}}({0}, groups={1})".format(str(self._inner), str(self._group))
        else:
            return "\mathrm{{CSMean}}({0})".format(str(self._inner))


cdef class CSPercentileSecurityValueHolder(CrossSectionValueHolder):

    def __init__(self, innerValue, groups=None):
        super(CSPercentileSecurityValueHolder, self).__init__(innerValue, groups)

    cdef _cal_impl(self):
        cdef SeriesValues raw_values = self._inner.value

        if self._group:
            self.cached = raw_values.percentile(self._group.value)
        else:
            self.cached = raw_values.percentile()
        self.updated = 1

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            self._cal_impl()
            return self.cached

    cpdef double value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            self._cal_impl()
            return self.cached[name]

    cpdef SeriesValues value_by_names(self, list names):
        cdef SeriesValues raw_values = self._inner.value_by_names(names)
        if self._group:
            raw_values = raw_values.percentile(self._group.value_by_names(names))
        else:
            raw_values = raw_values.percentile()
        return raw_values

    def __str__(self):
        if self._group:
            return "\mathrm{{CSPercentile}}({0}, groups={1})".format(str(self._inner), str(self._group))
        else:
            return "\mathrm{{CSPercentile}}({0})".format(str(self._inner))


cdef class CSAverageAdjustedSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue, groups=None):
        super(CSAverageAdjustedSecurityValueHolder, self).__init__(innerValue, groups)

    @property
    def value(self):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            if self._group:
                self.cached = raw_values - raw_values.mean(self._group.value)
            else:
                self.cached = raw_values - raw_values.mean()
            self.updated = 1
            return self.cached

    cpdef double value_by_name(self, name):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            if self._group:
                self.cached = raw_values - raw_values.mean(self._group.value)
            else:
                self.cached = raw_values - raw_values.mean()
            self.updated = 1
            return self.cached[name]

    cpdef SeriesValues value_by_names(self, list names):
        raw_values = self._inner.value_by_names(names)
        if self._group:
            self.cached = raw_values - raw_values.mean(self._group.value)
        else:
            self.cached = raw_values - raw_values.mean()
        return raw_values[names]

    def __str__(self):
        if self._group:
            return "\mathrm{{CSMeanAdjusted}}({0}, groups={1})".format(str(self._inner), str(self._group))
        else:
            return "\mathrm{{CSMeanAdjusted}}({0})".format(str(self._inner))


cdef class CSZScoreSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue, groups=None):
        super(CSZScoreSecurityValueHolder, self).__init__(innerValue, groups)

    cdef _cal_impl(self):
        cdef SeriesValues raw_values = self._inner.value

        if self._group:
            self.cached = raw_values.zscore(self._group.value)
        else:
            self.cached = raw_values.zscore()
        self.updated = 1

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            self._cal_impl()
            return self.cached

    cpdef double value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            self._cal_impl()
            return self.cached[name]

    cpdef SeriesValues value_by_names(self, list names):
        cdef SeriesValues raw_values = self._inner.value_by_names(names)
        if self._group:
            raw_values = raw_values.zscore(self._group.value_by_names(names))
        else:
            raw_values = raw_values.zscore()
        return raw_values

    def __str__(self):
        if self._group:
            return "\mathrm{{CSZscore}}({0}, groups={1})".format(str(self._inner), str(self._group))
        else:
            return "\mathrm{{CSZscore}}({0})".format(str(self._inner))


cdef class CSResidueSecurityValueHolder(SecurityValueHolder):

    cdef public SecurityValueHolder _left
    cdef public SecurityValueHolder _right

    def __init__(self, left, right):
        super(CSResidueSecurityValueHolder, self).__init__()
        self._left = build_holder(left)
        self._right = build_holder(right)

        self._window = max(self._left.window, self._right.window)
        self._dependency = list(set(self._left.fields + self._right.fields))
        self.updated = 0
        self.cached = None

    @property
    def symbolList(self):
        return self._left.symbolList

    cpdef push(self, dict data):
        self._left.push(data)
        self._right.push(data)
        self.updated = 0

    @property
    def value(self):

        cdef SeriesValues left_raw_values
        cdef SeriesValues right_raw_values

        if self.updated:
            return self.cached
        else:
            left_raw_values = self._left.value
            right_raw_values = self._right.value
            self.cached = left_raw_values.res(right_raw_values)
            self.updated = 1
            return self.cached

    cpdef double value_by_name(self, name):

        cdef SeriesValues left_raw_values
        cdef SeriesValues right_raw_values

        if self.updated:
            return self.cached[name]
        else:
            left_raw_values = self._left.value
            right_raw_values = self._right.value
            self.cached = left_raw_values.res(right_raw_values)
            self.updated = 1
            return self.cached[name]

    cpdef SeriesValues value_by_names(self, list names):
        cdef SeriesValues left_raw_values
        cdef SeriesValues right_raw_values
        left_raw_values = self._left.value_by_names(names)
        right_raw_values = self._right.value_by_names(names)
        raw_values = left_raw_values.res(right_raw_values)
        return raw_values

    def __str__(self):
        return "\mathrm{{CSRes}}({0}, {1})".format(str(self._left), str(self._right))
