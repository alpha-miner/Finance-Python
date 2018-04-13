# -*- coding: utf-8 -*-
u"""
Created on 2017-2-10

@author: cheng.li
"""

cimport numpy as np
from PyFin.Math.Accumulators.impl cimport Deque
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator


cdef class StatefulValueHolder(Accumulator):

    cdef public Deque _deque

    cpdef size_t size(self)
    cpdef bint isFull(self)


cdef class Shift(StatefulValueHolder):

    cdef public double _popout
    cdef public Accumulator _x

    cpdef int lag(self)
    cpdef push(self, dict data)
    cpdef double result(self)


cdef class SingleValuedValueHolder(StatefulValueHolder):

    cdef public Accumulator _x


cdef class SortedValueHolder(SingleValuedValueHolder):

    cdef list _sortedArray
    cdef double _cur_pos
    cpdef push(self, dict data)

cdef class MovingMax(SortedValueHolder):

    cpdef double result(self)


cdef class MovingMin(SortedValueHolder):

    cpdef double result(self)


cdef class MovingRank(SortedValueHolder):

    cpdef double result(self)


cdef class MovingQuantile(SortedValueHolder):

    cpdef double result(self)


cdef class MovingAllTrue(SingleValuedValueHolder):

    cdef public size_t _countedTrue

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingAnyTrue(SingleValuedValueHolder):

    cdef public size_t _countedTrue

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingSum(SingleValuedValueHolder):

    cdef public double _runningSum

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingAverage(SingleValuedValueHolder):

    cdef public double _runningSum

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingPositiveAverage(SingleValuedValueHolder):

    cdef public double _runningPositiveSum
    cdef public int _runningPositiveCount

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingPositiveDifferenceAverage(SingleValuedValueHolder):

    cdef public MovingAverage _runningAverage

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingNegativeDifferenceAverage(SingleValuedValueHolder):

    cdef public MovingAverage _runningAverage

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingRSI(SingleValuedValueHolder):

    cdef public MovingPositiveDifferenceAverage _posDiffAvg
    cdef public MovingNegativeDifferenceAverage _negDiffAvg

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingNegativeAverage(SingleValuedValueHolder):

    cdef public double _runningNegativeSum
    cdef public int _runningNegativeCount

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingVariance(SingleValuedValueHolder):

    cdef public double _runningSum
    cdef public double _runningSumSquare
    cdef public int _isPop

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingStandardDeviation(SingleValuedValueHolder):

    cdef public double _runningSum
    cdef public double _runningSumSquare
    cdef public int _isPop

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingNegativeVariance(SingleValuedValueHolder):

    cdef public double _runningNegativeSum
    cdef public double _runningNegativeSumSquare
    cdef public int _runningNegativeCount
    cdef public int _isPop

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingCountedPositive(SingleValuedValueHolder):

    cdef public int _counts

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingCountedNegative(SingleValuedValueHolder):

    cdef public int _counts

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingCorrelation(StatefulValueHolder):

    cdef public double _runningSumLeft
    cdef public double _runningSumRight
    cdef public double _runningSumSquareLeft
    cdef public double _runningSumSquareRight
    cdef public double _runningSumCrossSquare
    cdef Accumulator _x
    cdef Accumulator _y
    cdef Deque _deque_y

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingProduct(SingleValuedValueHolder):

    cdef public double _runningProduct

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MACD(Accumulator):

    cdef public Accumulator _short_average
    cdef public Accumulator _long_average

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingLogReturn(SingleValuedValueHolder):

    cdef public double _runningReturn

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingSharp(StatefulValueHolder):

    cdef public MovingAverage _mean
    cdef public MovingVariance _var
    cdef Accumulator _x
    cdef Accumulator _y
    cdef Deque _deque_y

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingSortino(StatefulValueHolder):

    cdef public MovingAverage _mean
    cdef public MovingNegativeVariance _negativeVar
    cdef Accumulator _x
    cdef Accumulator _y
    cdef Deque _deque_y

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingDrawdown(StatefulValueHolder):

    cdef MovingMax _maxer
    cdef double _runningCum
    cdef double _currentMax
    cdef Accumulator _x

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingMaxDrawdown(StatefulValueHolder):

    cdef MovingDrawdown _drawdownCalculator
    cdef MovingMin _minimer
    cdef Accumulator _x

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class MovingResidue(StatefulValueHolder):

    cdef public double _cross
    cdef public double _xsquare
    cdef public double _lastx
    cdef public double _lasty
    cdef Accumulator _x
    cdef Accumulator _y
    cdef Deque _deque_y

    cpdef push(self, dict data)
    cpdef double result(self)
    cpdef bint isFull(self)
