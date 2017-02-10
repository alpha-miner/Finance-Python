# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""


cdef class IAccumulator(object):
    pass


cdef class Accumulator(IAccumulator):

    cdef public int _isFull
    cdef public object _dependency
    cdef public int _isValueHolderContained
    cdef public int _window
    cdef public int _returnSize

    cdef extract(self, dict data)
    cpdef push(self, dict data)


cdef class StatelessSingleValueAccumulator(Accumulator):

    cdef _push(self, dict data)


cpdef build_holder(name)


cdef class Negative(Accumulator):

    cdef public Accumulator _valueHolder

    cpdef push(self, dict data)
    cpdef result(self)


cdef class ListedValueHolder(Accumulator):

    cdef public Accumulator _left
    cdef public Accumulator _right

    cpdef push(self, dict data)
    cpdef result(self)


cdef class TruncatedValueHolder(Accumulator):

    cdef public int _start
    cdef public int _stop
    cdef public Accumulator _valueHolder

    cpdef push(self, dict data)
    cpdef result(self)


cdef class CombinedValueHolder(Accumulator):

    cdef public Accumulator _left
    cdef public Accumulator _right

    cpdef push(self, dict data)


cdef class AddedValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class MinusedValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class MultipliedValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class DividedValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class LtOperatorValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class LeOperatorValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class GtOperatorValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class GeOperatorValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class EqOperatorValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class NeOperatorValueHolder(CombinedValueHolder):

    cpdef result(self)


cdef class Identity(Accumulator):

    cdef public double _value

    cpdef push(self, dict data)
    cpdef result(self)


cdef class Latest(StatelessSingleValueAccumulator):

    cdef public double _latest

    cpdef push(self, dict data)
    cpdef result(self)


cdef class CompoundedValueHolder(Accumulator):

    cdef public Accumulator _left
    cdef public Accumulator _right

    cpdef push(self, dict data)
    cpdef result(self)


cdef class IIF(Accumulator):

    cdef public Accumulator _cond
    cdef public Accumulator _left
    cdef public Accumulator _right

    cpdef push(self, dict data)
    cpdef result(self)


cdef class BasicFunction(Accumulator):

    cdef public double _origValue

    cpdef push(self, dict data)


cdef class Exp(BasicFunction):

    cpdef double result(self)


cdef class Log(BasicFunction):

    cpdef double result(self)


cdef class Sqrt(BasicFunction):

    cpdef double result(self)


cdef class Pow(BasicFunction):

    cdef public double _n

    cpdef double result(self)


cdef class Abs(BasicFunction):

    cpdef double result(self)


cdef class Sign(BasicFunction):

    cpdef double result(self)


cdef class Acos(BasicFunction):

    cpdef double result(self)


cdef class Acosh(BasicFunction):

    cpdef double result(self)


cdef class Asin(BasicFunction):

    cpdef double result(self)


cdef class Asinh(BasicFunction):

    cpdef double result(self)