# -*- coding: utf-8 -*-
u"""
Created on 2017-2-10

@author: cheng.li
"""

cimport numpy as np
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Math.Accumulators.IAccumulators cimport StatelessSingleValueAccumulator


cdef class Diff(StatelessSingleValueAccumulator):

    cdef public double _curr
    cdef public double _previous

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class SimpleReturn(StatelessSingleValueAccumulator):

    cdef public double _diff
    cdef public double _curr
    cdef public double _previous

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class LogReturn(StatelessSingleValueAccumulator):

    cdef public double _diff
    cdef public double _curr
    cdef public double _previous

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class PositivePart(StatelessSingleValueAccumulator):

    cdef public double _pos

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class NegativePart(StatelessSingleValueAccumulator):

    cdef public double _neg

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Max(StatelessSingleValueAccumulator):

    cdef public double _currentMax
    cdef public int _first

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Maximum(StatelessSingleValueAccumulator):

    cdef public double _currentMax

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Min(StatelessSingleValueAccumulator):

    cdef public double _currentMin
    cdef public int _first

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Minimum(StatelessSingleValueAccumulator):

    cdef public double _currentMin
    cdef public int _first

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Sum(StatelessSingleValueAccumulator):

    cdef public double _currentSum
    cdef public int _first

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Average(StatelessSingleValueAccumulator):

    cdef public double _currentSum
    cdef public int _currentCount

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class XAverage(StatelessSingleValueAccumulator):

    cdef public double _average
    cdef public double _exp
    cdef public int _count

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Variance(StatelessSingleValueAccumulator):

    cdef public double _currentSum
    cdef public double _currentSumSquare
    cdef public int _currentCount
    cdef public bint _isPop

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Product(StatelessSingleValueAccumulator):

    cdef public double _product

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class CenterMoment(StatelessSingleValueAccumulator):

    cdef public list _this_list
    cdef public double _order
    cdef public double _moment

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Skewness(StatelessSingleValueAccumulator):

    cdef public Accumulator _skewness

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Kurtosis(StatelessSingleValueAccumulator):

    cdef public Accumulator _kurtosis

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Rank(StatelessSingleValueAccumulator):

    cdef public list _thisList
    cdef public list _sortedList
    cdef public list _rank

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class LevelList(StatelessSingleValueAccumulator):

    cdef public list _levelList
    cdef public list _thisList

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class LevelValue(StatelessSingleValueAccumulator):

    cdef public list _thisList
    cdef public double _levelValue

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class AutoCorrelation(StatelessSingleValueAccumulator):

    cdef public int _lags
    cdef public list _thisList
    cdef public list _VecForward
    cdef public list _VecBackward
    cdef public np.ndarray _AutoCorrMatrix

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class StatelessMultiValueAccumulator(Accumulator):

    cdef _push(self, dict data)


cdef class Correlation(StatelessMultiValueAccumulator):

    cdef public double _runningSumLeft
    cdef public double _runningSumRight
    cdef public double _runningSumSquareLeft
    cdef public double _runningSumSquareRight
    cdef public double _runningSumCrossSquare
    cdef public int _currentCount

    cpdef push(self, dict data)
    cpdef object result(self)