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
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingCorrelation
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingRank
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


cdef class SecurityMovingAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingAverage, self).__init__(window, MovingAverage, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MA}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingMax(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingMax, self).__init__(window, MovingMax, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MMax}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingMin(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingMin, self).__init__(window, MovingMin, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MMin}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingQuantile(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingQuantile, self).__init__(window, MovingQuantile, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MQuantile}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingAllTrue(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingAllTrue, self).__init__(window, MovingAllTrue, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MAllTrue}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingAnyTrue(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingAnyTrue, self).__init__(window, MovingAnyTrue, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MAnyTrue}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingSum(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingSum, self).__init__(window, MovingSum, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MSum}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingVariance(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingVariance, self).__init__(window, MovingVariance, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MVariance}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingStandardDeviation(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingStandardDeviation, self).__init__(window, MovingStandardDeviation, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MStd}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingCountedPositive(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingCountedPositive, self).__init__(window, MovingCountedPositive, dependency)


cdef class SecurityMovingPositiveAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingPositiveAverage, self).__init__(window, MovingPositiveAverage, dependency)


cdef class SecurityMovingCountedNegative(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingCountedNegative, self).__init__(window, MovingCountedNegative, dependency)


cdef class SecurityMovingNegativeAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingNegativeAverage, self).__init__(window, MovingNegativeAverage, dependency)


cdef class SecurityMovingPositiveDifferenceAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingPositiveDifferenceAverage, self).__init__(window, MovingPositiveDifferenceAverage, dependency)


cdef class SecurityMovingNegativeDifferenceAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingNegativeDifferenceAverage, self).__init__(window, MovingNegativeDifferenceAverage, dependency)


cdef class SecurityMovingRSI(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingRSI, self).__init__(window, MovingRSI, dependency)


cdef class SecurityMovingLogReturn(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingLogReturn, self).__init__(window, MovingLogReturn, dependency)


cdef class SecurityMovingResidue(SecuritySingleValueHolder):
    def __init__(self, window, dependency=('y', 'x')):
        super(SecurityMovingResidue, self).__init__(window, MovingResidue, dependency)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{Res}}({0}, {1})".format(self._window - self._compHolder._window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingCorrelation(SecuritySingleValueHolder):
    def __init__(self, window, dependency=('y', 'x')):
        super(SecurityMovingCorrelation, self).__init__(window, MovingCorrelation, dependency)


cdef class SecurityMovingRank(SecuritySingleValueHolder):

    def __init__(self, window, dependency='x'):
        super(SecurityMovingRank, self).__init__(window, MovingRank, dependency)


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
