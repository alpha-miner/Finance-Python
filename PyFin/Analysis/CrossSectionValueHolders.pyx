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
from PyFin.Analysis.SecurityValueHolders cimport SecurityLatestValueHolder


cdef class CrossSectionValueHolder(SecurityValueHolder):

    cdef public SecurityValueHolder _inner

    def __init__(self, innerValue):
        if isinstance(innerValue, SecurityValueHolder):
            self._inner = copy.deepcopy(innerValue)
        elif isinstance(innerValue, six.string_types):
            self._inner = SecurityLatestValueHolder(innerValue)
        else:
            raise ValueError("Currently only value holder input is allowed for rank holder.")
        self._window = self._inner.window
        self._returnSize = self._inner.valueSize
        self._dependency = copy.deepcopy(self._inner._dependency)
        self.updated = 0
        self.cached = None

    @property
    def symbolList(self):
        return self._inner.symbolList

    @property
    def holders(self):
        return self._inner.holders

    cpdef push(self, dict data):
        self._inner.push(data)
        self.updated = 0


cdef class CSRankedSecurityValueHolder(CrossSectionValueHolder):

    def __init__(self, innerValue):
        super(CSRankedSecurityValueHolder, self).__init__(innerValue)

    @property
    def value(self):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            self.cached = raw_values.rank()
            self.updated = 1
            return self.cached

    cpdef value_by_name(self, name):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            self.cached = raw_values.rank()
            self.updated = 1
            return self.cached[name]

    cpdef value_by_names(self, list names):
        cdef SeriesValues raw_values
        raw_values = self._inner.value_by_names(names)
        raw_values = raw_values.rank()
        return raw_values

    def __deepcopy__(self, memo):
        return CSRankedSecurityValueHolder(self._inner)

    def __reduce__(self):
        d = {}
        return CSRankedSecurityValueHolder, (self._inner, ), d

    def __setstate__(self, state):
        pass


cdef class CSAverageSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue):
        super(CSAverageSecurityValueHolder, self).__init__(innerValue)

    @property
    def value(self):

        cdef SeriesValues raw_values
        cdef np.ndarray[double, ndim=1] mean_value

        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            mean_value = np.array([raw_values.mean()] * len(raw_values))
            mean_value[np.isnan(raw_values.values)] = np.nan
            self.cached = SeriesValues(mean_value, raw_values.name_mapping)
            self.updated = 1
            return self.cached

    cpdef value_by_name(self, name):

        cdef SeriesValues raw_values
        cdef np.ndarray[double, ndim=1] mean_value

        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            mean_value = np.array([raw_values.mean()] * len(raw_values))
            mean_value[np.isnan(raw_values.values)] = np.nan
            self.cached = SeriesValues(mean_value, raw_values.name_mapping)
            self.updated = 1
            return self.cached[name]

    cpdef value_by_names(self, list names):

        cdef SeriesValues raw_values
        cdef np.ndarray[double, ndim=1] mean_value

        raw_values = self._inner.value_by_names(names)
        mean_value = np.array([raw_values.mean()] * len(raw_values))
        mean_value[np.isnan(raw_values.values)] = np.nan
        raw_values = SeriesValues(mean_value, raw_values.name_mapping)
        return raw_values[names]

    def __deepcopy__(self, memo):
        return CSAverageSecurityValueHolder(self._inner)

    def __reduce__(self):
        d = {}
        return CSAverageSecurityValueHolder, (self._inner, ), d

    def __setstate__(self, state):
        pass


cdef class CSAverageAdjustedSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue):
        super(CSAverageAdjustedSecurityValueHolder, self).__init__(innerValue)

    @property
    def value(self):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            self.cached = raw_values - raw_values.mean()
            self.updated = 1
            return self.cached

    cpdef value_by_name(self, name):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            self.cached = raw_values - raw_values.mean()
            self.updated = 1
            return self.cached[name]

    cpdef value_by_names(self, list names):
        raw_values = self._inner.value_by_names(names)
        raw_values = raw_values - raw_values.mean()
        return raw_values[names]

    def __deepcopy__(self, memo):
        return CSAverageAdjustedSecurityValueHolder(self._inner)

    def __reduce__(self):
        d = {}
        return CSAverageAdjustedSecurityValueHolder, (self._inner, ), d

    def __setstate__(self, state):
        pass


cdef class CSQuantileSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue):
        super(CSQuantileSecurityValueHolder, self).__init__(innerValue)

    @property
    def value(self):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            self.cached = (raw_values.rank() - 1.) / (len(raw_values) - 1.)
            self.updated = 1
            return self.cached

    @cython.cdivision(True)
    cpdef value_by_name(self, name):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            self.cached = (raw_values.rank() - 1.) / (len(raw_values) - 1.)
            self.updated = 1
            return self.cached[name]

    @cython.cdivision(True)
    cpdef value_by_names(self, list names):

        cdef SeriesValues raw_values

        raw_values = self._inner.value_by_names(names)
        raw_values = (raw_values.rank() - 1.) / (len(raw_values) - 1.)
        return raw_values[names]

    def __deepcopy__(self, memo):
        return CSQuantileSecurityValueHolder(self._inner)

    def __reduce__(self):
        d = {}
        return CSQuantileSecurityValueHolder, (self._inner, ), d

    def __setstate__(self, state):
        pass


cdef class CSZScoreSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue):
        super(CSZScoreSecurityValueHolder, self).__init__(innerValue)

    @property
    def value(self):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            self.cached = raw_values.zscore()
            self.updated = 1
            return self.cached

    @cython.cdivision(True)
    cpdef value_by_name(self, name):

        cdef SeriesValues raw_values

        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            self.cached = raw_values.zscore()
            self.updated = 1
            return self.cached[name]

    @cython.cdivision(True)
    cpdef value_by_names(self, list names):

        cdef SeriesValues raw_values

        raw_values = self._inner.value_by_names(names)
        raw_values = raw_values.zscore()
        return raw_values[names]

    def __deepcopy__(self, memo):
        return CSZScoreSecurityValueHolder(self._inner)

    def __reduce__(self):
        d = {}
        return CSZScoreSecurityValueHolder, (self._inner, ), d

    def __setstate__(self, state):
        pass
