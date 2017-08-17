# -*- coding: utf-8 -*-
u"""
Created on 2017-2-10

@author: cheng.li
"""

cimport numpy as np
from PyFin.Math.Accumulators.impl cimport Deque
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Math.Accumulators.IAccumulators cimport StatelessSingleValueAccumulator


cdef class StatefulValueHolder(Accumulator):

    cdef public Deque _deque

    cpdef size_t size(self)
    cpdef bint isFull(self)
    cpdef copy_attributes(self, dict attributes, bint is_deep=*)
    cpdef collect_attributes(self)


cdef class Shift(StatefulValueHolder):

    cdef public Accumulator _valueHolder
    cdef public double _popout

    cpdef int lag(self)
    cpdef push(self, dict data)
    cpdef object result(self)


cdef class SingleValuedValueHolder(StatefulValueHolder):

    cpdef double _push(self, dict data)


cdef class SortedValueHolder(SingleValuedValueHolder):

    cdef public list _sortedArray

    cpdef push(self, dict data)
    cpdef copy_attributes(self, dict attributes, bint is_deep=*)
    cpdef collect_attributes(self)


cdef class MovingMax(SortedValueHolder):

    cpdef object result(self)


cdef class MovingMin(SortedValueHolder):

    cpdef object result(self)


cdef class MovingQuantile(SortedValueHolder):

    cpdef object result(self)


cdef class MovingAllTrue(SingleValuedValueHolder):

    cdef public size_t _countedTrue

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingAnyTrue(SingleValuedValueHolder):

    cdef public size_t _countedTrue

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingSum(SingleValuedValueHolder):

    cdef public double _runningSum

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingAverage(SingleValuedValueHolder):

    cdef public double _runningSum

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingPositiveAverage(SingleValuedValueHolder):

    cdef public double _runningPositiveSum
    cdef public int _runningPositiveCount

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingPositiveDifferenceAverage(SingleValuedValueHolder):

    cdef public MovingAverage _runningAverage

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingNegativeDifferenceAverage(SingleValuedValueHolder):

    cdef public MovingAverage _runningAverage

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingRSI(SingleValuedValueHolder):

    cdef public MovingPositiveDifferenceAverage _posDiffAvg
    cdef public MovingNegativeDifferenceAverage _negDiffAvg

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingNegativeAverage(SingleValuedValueHolder):

    cdef public double _runningNegativeSum
    cdef public int _runningNegativeCount

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingVariance(SingleValuedValueHolder):

    cdef public double _runningSum
    cdef public double _runningSumSquare
    cdef public int _isPop

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingStandardDeviation(SingleValuedValueHolder):

    cdef public double _runningSum
    cdef public double _runningSumSquare
    cdef public int _isPop

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingNegativeVariance(SingleValuedValueHolder):

    cdef public double _runningNegativeSum
    cdef public double _runningNegativeSumSquare
    cdef public int _runningNegativeCount
    cdef public int _isPop

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingCountedPositive(SingleValuedValueHolder):

    cdef public int _counts

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingCountedNegative(SingleValuedValueHolder):

    cdef public int _counts

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingHistoricalWindow(StatefulValueHolder):

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingCorrelation(StatefulValueHolder):

    cdef public double _runningSumLeft
    cdef public double _runningSumRight
    cdef public double _runningSumSquareLeft
    cdef public double _runningSumSquareRight
    cdef public double _runningSumCrossSquare

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingCorrelationMatrix(StatefulValueHolder):

    cdef public int _isFirst
    cdef public np.ndarray _runningSum
    cdef public np.ndarray _runningSumSquare
    cdef public np.ndarray _runningSumCrossSquare

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingProduct(SingleValuedValueHolder):

    cdef public double _runningProduct

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingCenterMoment(SingleValuedValueHolder):

    cdef public double _order
    cdef public double _runningMoment

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingSkewness(SingleValuedValueHolder):

    cdef public Accumulator _runningSkewness

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingMaxPos(SortedValueHolder):

    cdef public double _runningTsMaxPos
    cdef public double _max

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingMinPos(SortedValueHolder):

    cdef public double _runningTsMinPos
    cdef public double _min

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingKurtosis(SingleValuedValueHolder):

    cdef public Accumulator _runningKurtosis

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingRSV(SingleValuedValueHolder):

    cdef public double _cached_value

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MACD(StatelessSingleValueAccumulator):

    cdef public Accumulator _short_average
    cdef public Accumulator _long_average

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingRank(SortedValueHolder):

    cdef public list _runningRank

    cpdef object result(self)


cdef class MovingKDJ(StatefulValueHolder):

    cdef public MovingRSV _runningRsv
    cdef public int _k
    cdef public int _d
    cdef public double _runningJ
    cdef public double _runningD
    cdef public double _runningK

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingAroon(SingleValuedValueHolder):

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingBias(SingleValuedValueHolder):

    cdef public double _runningBias

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingLevel(SingleValuedValueHolder):

    cdef public double _runningLevel

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingAutoCorrelation(SingleValuedValueHolder):

    cdef public int _lags
    cdef public list _runningVecForward
    cdef public list _runningVecBackward
    cdef public np.ndarray _runningAutoCorrMatrix

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingLogReturn(SingleValuedValueHolder):

    cdef public double _runningReturn

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingSharp(StatefulValueHolder):

    cdef public MovingAverage _mean
    cdef public MovingVariance _var

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingSortino(StatefulValueHolder):

    cdef public MovingAverage _mean
    cdef public MovingNegativeVariance _negativeVar

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingResidue(StatefulValueHolder):

    cdef public double _cross
    cdef public double _xsquare
    cdef public double _lastx
    cdef public double _lasty

    cpdef push(self, dict data)
    cpdef object result(self)
    cpdef bint isFull(self)


cdef class MovingAlphaBeta(StatefulValueHolder):

    cdef public MovingAverage _pReturnMean
    cdef public MovingAverage _mReturnMean
    cdef public MovingVariance _pReturnVar
    cdef public MovingVariance _mReturnVar
    cdef public MovingCorrelation _correlationHolder

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingDrawDown(StatefulValueHolder):

    cdef public MovingMax _maxer
    cdef public double _runningCum
    cdef public double _currentMax
    cdef public int _highIndex
    cdef public int _runningIndex

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingAverageDrawdown(StatefulValueHolder):

    cdef public MovingDrawDown _drawdownCalculator
    cdef public MovingAverage _drawdownMean
    cdef public MovingAverage _durationMean

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class MovingMaxDrawdown(StatefulValueHolder):

    cdef public MovingDrawDown _drawdownCalculator

    cpdef push(self, dict data)
    cpdef object result(self)