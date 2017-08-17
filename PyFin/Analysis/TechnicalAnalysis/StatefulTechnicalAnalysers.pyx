# -*- coding: utf-8 -*-
u"""
Created on 2015-8-8

@author: cheng.li
"""

import copy
import numpy as np
cimport numpy as np
cimport cython
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Analysis.SeriesValues cimport SeriesValues
from PyFin.Analysis.SecurityValueHolders cimport SecurityValueHolder
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingMax
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingMin
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingQuantile
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingAllTrue
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingAnyTrue
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingSum
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingVariance
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingStandardDeviation
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingCountedPositive
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingPositiveAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingCountedNegative
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingNegativeAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingPositiveDifferenceAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingNegativeDifferenceAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingRSI
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingResidue
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingHistoricalWindow
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingLogReturn
from PyFin.Math.MathConstants cimport NAN


cdef class SecuritySingleValueHolder(SecurityValueHolder):
    def __init__(self, window, HolderType, dependency='x'):
        super(SecuritySingleValueHolder, self).__init__(dependency)
        self._window += window
        if self._compHolder:
            self._holderTemplate = HolderType(window=window, dependency='x')
            self._innerHolders = {
                name: copy.deepcopy(self._holderTemplate) for name in self._compHolder.symbolList
                }
        else:
            self._holderTemplate = HolderType(window=window, dependency=self._dependency)

    def __setstate__(self, state):
        self.copy_attributes(state, is_deep=False)


cdef class SecurityMovingAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingAverage, self).__init__(window, MovingAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingAverage(self._window, self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingAverage,(self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingAverage, (self._window, self._dependency), d


cdef class SecurityMovingMax(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingMax, self).__init__(window, MovingMax, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingMax(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingMax(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingMax, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingMax, (self._window, self._dependency), d


cdef class SecurityMovingMin(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingMin, self).__init__(window, MovingMin, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingMin(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingMin(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingMin, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingMin, (self._window, self._dependency), d


cdef class SecurityMovingQuantile(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingQuantile, self).__init__(window, MovingQuantile, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingQuantile(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingQuantile(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingQuantile, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingQuantile, (self._window, self._dependency), d


cdef class SecurityMovingAllTrue(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingAllTrue, self).__init__(window, MovingAllTrue, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingAllTrue(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingAllTrue(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingAllTrue, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingAllTrue, (self._window, self._dependency), d


cdef class SecurityMovingAnyTrue(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingAnyTrue, self).__init__(window, MovingAnyTrue, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingAnyTrue(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingAnyTrue(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingAnyTrue, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingAnyTrue, (self._window, self._dependency), d


cdef class SecurityMovingSum(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingSum, self).__init__(window, MovingSum, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingSum(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingSum(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingSum, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingSum, (self._window, self._dependency), d


cdef class SecurityMovingVariance(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingVariance, self).__init__(window, MovingVariance, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingVariance(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingVariance(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingVariance, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingVariance, (self._window, self._dependency), d


cdef class SecurityMovingStandardDeviation(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingStandardDeviation, self).__init__(window, MovingStandardDeviation, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingStandardDeviation(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingStandardDeviation(self._window, self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingStandardDeviation,(self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingStandardDeviation, (self._window, self._dependency), d


cdef class SecurityMovingCountedPositive(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingCountedPositive, self).__init__(window, MovingCountedPositive, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingCountedPositive(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingCountedPositive(self._window, self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingCountedPositive, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingCountedPositive, (self._window, self._dependency), d


cdef class SecurityMovingPositiveAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingPositiveAverage, self).__init__(window, MovingPositiveAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingPositiveAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingPositiveAverage(self._window, self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingPositiveAverage, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingPositiveAverage, (self._window, self._dependency), d


cdef class SecurityMovingCountedNegative(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingCountedNegative, self).__init__(window, MovingCountedNegative, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingCountedNegative(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingCountedNegative(self._window, self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingCountedNegative, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingCountedNegative, (self._window, self._dependency), d


cdef class SecurityMovingNegativeAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingNegativeAverage, self).__init__(window, MovingNegativeAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingNegativeAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingNegativeAverage(self._window, self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingNegativeAverage, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingNegativeAverage, (self._window, self._dependency), d


cdef class SecurityMovingPositiveDifferenceAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingPositiveDifferenceAverage, self).__init__(window, MovingPositiveDifferenceAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingPositiveDifferenceAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            copied =  SecurityMovingPositiveDifferenceAverage(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingPositiveDifferenceAverage, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingPositiveDifferenceAverage, (self._window, self._dependency), d


cdef class SecurityMovingNegativeDifferenceAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingNegativeDifferenceAverage, self).__init__(window, MovingNegativeDifferenceAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingNegativeDifferenceAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingNegativeDifferenceAverage(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingNegativeDifferenceAverage, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingNegativeDifferenceAverage, (self._window, self._dependency), d


cdef class SecurityMovingRSI(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingRSI, self).__init__(window, MovingRSI, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingRSI(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingRSI(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingRSI, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingRSI, (self._window, self._dependency), d


cdef class SecurityMovingLogReturn(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingLogReturn, self).__init__(window, MovingLogReturn, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingLogReturn(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingLogReturn(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingLogReturn, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingLogReturn, (self._window, self._dependency), d


cdef class SecurityMovingResidue(SecuritySingleValueHolder):
    def __init__(self, window, dependency=('y', 'x')):
        super(SecurityMovingResidue, self).__init__(window, MovingResidue, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingResidue(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingResidue(self._window, self._dependency)
        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingResidue, (self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingResidue, (self._window, self._dependency), d


cdef class SecurityMovingHistoricalWindow(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingHistoricalWindow, self).__init__(window, MovingHistoricalWindow, dependency)

    def __getitem__(self, item):
        if isinstance(item, str):
            return super(SecurityMovingHistoricalWindow, self).__getitem__(item)
        elif isinstance(item, int):
            res = {}
            for name in self._innerHolders:
                try:
                    res[name] = self._innerHolders[name].value[item]
                except ArithmeticError:
                    res[name] = NAN
            return SeriesValues(res)
        else:
            raise ValueError("{0} is not recognized as valid int or string".format(item))

    @property
    @cython.boundscheck(False)
    @cython.wraparound(False)
    def value(self):

        cdef list values
        cdef Accumulator holder
        cdef size_t n
        cdef int i

        if self.updated:
            return SeriesValues(self.cached.values, self.cached.name_mapping)
        else:
            keys = self._innerHolders.keys()
            n = len(keys)
            values = [None] * n
            for i, name in enumerate(keys):
                try:
                    holder = self._innerHolders[name]
                    values[i] = holder.result()
                except ArithmeticError:
                    values[i] = NAN
            self.cached = SeriesValues(np.array(values), index=dict(zip(keys, range(n))))
            self.updated = 1
            return self.cached

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef value_by_names(self, list names):
        cdef Accumulator holder
        cdef list res
        cdef int i
        cdef size_t n

        if self.updated:
            return self.cached[names]
        else:
            n = len(names)
            res = [None] * n
            for i, name in enumerate(names):
                holder = self._innerHolders[name]
                res[i] = holder.result()
            return SeriesValues(np.array(res), index=dict(zip(names, range(n))))

    cpdef value_by_name(self, name):
        cdef Accumulator holder
        if self.updated:
            return self.cached[name]
        else:
            holder = self._innerHolders[name]
            return holder.result()

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityMovingHistoricalWindow(self._window - self._compHolder._window, self._compHolder)
        else:
            copied = SecurityMovingHistoricalWindow(self._window, self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityMovingHistoricalWindow,(self._window - self._compHolder._window, self._compHolder), d
        else:
            return SecurityMovingHistoricalWindow, (self._window, self._dependency), d
