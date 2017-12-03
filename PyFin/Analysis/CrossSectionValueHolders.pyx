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
from PyFin.Analysis.SeriesValues cimport residue
from PyFin.Analysis.SecurityValueHolders cimport SecurityValueHolder
from PyFin.Analysis.SecurityValueHolders cimport SecurityLatestValueHolder
from PyFin.Analysis.SecurityValueHolders import _merge2set
from PyFin.Math.MathConstants cimport NAN


cdef class CrossSectionValueHolder(SecurityValueHolder):

    cdef public SecurityValueHolder _inner

    def __init__(self, innerValue):
        if isinstance(innerValue, SecurityValueHolder):
            self._inner = copy.deepcopy(innerValue)
        elif isinstance(innerValue, six.string_types):
            self._inner = SecurityLatestValueHolder(innerValue)
        else:
            raise ValueError("Currently only value holder input is allowed for cross sectional value holder.")
        self._window = self._inner.window
        self._returnSize = self._inner.valueSize
        self._dependency = copy.deepcopy(self._inner._dependency)
        self.updated = 0
        self.cached = None

    @property
    def symbolList(self):
        return self._inner.symbolList

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

    def __str__(self):
        return "\mathrm{{CSRank}}({0})".format(str(self._inner))

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
            mean_value[np.isnan(raw_values.values)] = NAN
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
            mean_value[np.isnan(raw_values.values)] = NAN
            self.cached = SeriesValues(mean_value, raw_values.name_mapping)
            self.updated = 1
            return self.cached[name]

    cpdef value_by_names(self, list names):

        cdef SeriesValues raw_values
        cdef np.ndarray[double, ndim=1] mean_value

        raw_values = self._inner.value_by_names(names)
        mean_value = np.array([raw_values.mean()] * len(raw_values))
        mean_value[np.isnan(raw_values.values)] = NAN
        raw_values = SeriesValues(mean_value, raw_values.name_mapping)
        return raw_values[names]

    def __str__(self):
        return "\mathrm{{CSMean}}({0})".format(str(self._inner))

    def __deepcopy__(self, memo):
        return CSAverageSecurityValueHolder(self._inner)

    def __reduce__(self):
        d = {}
        return CSAverageSecurityValueHolder, (self._inner, ), d

    def __setstate__(self, state):
        pass


cdef class CSPercentileSecurityValueHolder(CrossSectionValueHolder):

    cdef double percentile

    def __init__(self, percentile, innerValue):
        super(CSPercentileSecurityValueHolder, self).__init__(innerValue)
        self.percentile = percentile

    @property
    def value(self):

        cdef SeriesValues raw_values
        cdef np.ndarray[double, ndim=1] per_value

        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            per_value = np.array([raw_values.percentile(self.percentile)] * len(raw_values))
            per_value[np.isnan(raw_values.values)] = NAN
            self.cached = SeriesValues(per_value, raw_values.name_mapping)
            self.updated = 1
            return self.cached

    cpdef value_by_name(self, name):

        cdef SeriesValues raw_values
        cdef np.ndarray[double, ndim=1] per_value

        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            per_value = np.array([raw_values.percentile(self.percentile)] * len(raw_values))
            per_value[np.isnan(raw_values.values)] = NAN
            self.cached = SeriesValues(per_value, raw_values.name_mapping)
            self.updated = 1
            return self.cached[name]

    cpdef value_by_names(self, list names):

        cdef SeriesValues raw_values
        cdef np.ndarray[double, ndim=1] per_value

        raw_values = self._inner.value_by_names(names)
        per_value = np.array([raw_values.percentile(self.percentile)] * len(raw_values))
        per_value[np.isnan(raw_values.values)] = NAN
        raw_values = SeriesValues(per_value, raw_values.name_mapping)
        return raw_values[names]

    def __str__(self):
        return "\mathrm{{CSPercentile}}({0})".format(str(self._inner))

    def __deepcopy__(self, memo):
        return CSPercentileSecurityValueHolder(self.percentile, self._inner)

    def __reduce__(self):
        d = {}
        return CSPercentileSecurityValueHolder, (self.percentile, self._inner), d

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

    def __str__(self):
        return "\mathrm{{CSMeanAdjusted}}({0})".format(str(self._inner))

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

    def __str__(self):
        return "\mathrm{{CSQuantiles}}({0})".format(str(self._inner))

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

    def __str__(self):
        return "\mathrm{{CSZScore}}({0})".format(str(self._inner))

    def __deepcopy__(self, memo):
        return CSZScoreSecurityValueHolder(self._inner)

    def __reduce__(self):
        d = {}
        return CSZScoreSecurityValueHolder, (self._inner, ), d

    def __setstate__(self, state):
        pass


cdef class CrossBinarySectionValueHolder(SecurityValueHolder):

    cdef public SecurityValueHolder _left
    cdef public SecurityValueHolder _right

    def __init__(self, left, right):
        if isinstance(left, SecurityValueHolder):
            self._left = copy.deepcopy(left)
        elif isinstance(left, six.string_types):
            self._left = SecurityLatestValueHolder(left)
        else:
            raise ValueError("Currently only value holder input is allowed for binary cross sectional value holder.")

        if isinstance(right, SecurityValueHolder):
            self._right = copy.deepcopy(right)
        elif isinstance(right, six.string_types):
            self._right = SecurityLatestValueHolder(right)
        else:
            raise ValueError("Currently only value holder input is allowed for binary cross sectional value holder.")

        self._window = max(self._left.window, self._right._window)
        self._returnSize = self._left.valueSize
        self._dependency = _merge2set(self._left._dependency, self._right._dependency)
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
            self.cached = self.op(left_raw_values, right_raw_values)
            self.updated = 1
            return self.cached

    cpdef value_by_name(self, name):

        cdef SeriesValues left_raw_values
        cdef SeriesValues right_raw_values

        if self.updated:
            return self.cached[name]
        else:
            left_raw_values = self._left.value
            right_raw_values = self._right.value
            self.cached = self.op(left_raw_values, right_raw_values)
            self.updated = 1
            return self.cached[name]

    cpdef value_by_names(self, list names):
        cdef SeriesValues left_raw_values
        cdef SeriesValues right_raw_values
        left_raw_values = self._left.value_by_names(names)
        right_raw_values = self._right.value_by_names(names)
        raw_values = self.op(left_raw_values, right_raw_values)
        return raw_values

    def __deepcopy__(self, memo):
        return CrossBinarySectionValueHolder(self._left, self._right, self.op)

    def __reduce__(self):
        d = {}
        return CrossBinarySectionValueHolder, (self._left, self._right, self.op), d

    def __setstate__(self, state):
        pass


cdef class CSResidueSecurityValueHolder(CrossBinarySectionValueHolder):

    cdef public object op

    def __init__(self, left, right):
        super(CSResidueSecurityValueHolder, self).__init__(left, right)
        self.op = residue

    def __str__(self):
        return "\mathrm{{CSRes}}({0}, {1})".format(str(self._left), str(self._right))

    def __deepcopy__(self, memo):
        return CSResidueSecurityValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return CSResidueSecurityValueHolder, (self._left, self._right), d
