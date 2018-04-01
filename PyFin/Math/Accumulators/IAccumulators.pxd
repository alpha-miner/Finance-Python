# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""


cdef class IAccumulator(object):
    pass


cdef class Accumulator(IAccumulator):

    cdef public bint _isFull
    cdef public list _dependency
    cdef public size_t _window

    cpdef bint isFull(self)
    cpdef push(self, dict data)
    cpdef double result(self)
    cpdef transform(self, data, str name=*, bint to_sort=*)

cdef bint isanumber(a)
cpdef build_holder(name)


cdef class Negative(Accumulator):

    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class CombinedValueHolder(Accumulator):

    cdef Accumulator _left
    cdef Accumulator _right

    cpdef push(self, dict data)


cdef class AddedValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class MinusedValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class MultipliedValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class DividedValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class LtOperatorValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class LeOperatorValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class GtOperatorValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class GeOperatorValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class EqOperatorValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class NeOperatorValueHolder(CombinedValueHolder):

    cpdef double result(self)


cdef class Identity(Accumulator):

    cdef double _value

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class Latest(Accumulator):

    cdef double _latest

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class CompoundedValueHolder(Accumulator):

    cdef Accumulator _left
    cdef Accumulator _right

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class IIF(Accumulator):

    cdef Accumulator _cond
    cdef Accumulator _left
    cdef Accumulator _right

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class BasicFunction(Accumulator):

    cdef double _origValue
    cdef Accumulator _inner

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