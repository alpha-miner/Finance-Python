# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""


cdef class IAccumulator(object):
    pass


cdef class Accumulator(IAccumulator):

    cdef public bint _isFull
    cdef public object _dependency
    cdef public bint _isValueHolderContained
    cdef public size_t _window
    cdef public size_t _returnSize

    cpdef bint isFull(self)
    cdef extract(self, dict data)
    cpdef push(self, dict data)
    cpdef object result(self)
    cpdef transform(self, data, str name=*, bint to_sort=*)
    cpdef copy_attributes(self, dict attributes, bint is_deep=*)
    cpdef collect_attributes(self)

cdef class StatelessSingleValueAccumulator(Accumulator):

    cdef _push(self, dict data)


cpdef build_holder(name)


cdef class Negative(Accumulator):

    cdef public Accumulator _valueHolder

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class ListedValueHolder(Accumulator):

    cdef public Accumulator _left
    cdef public Accumulator _right

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class TruncatedValueHolder(Accumulator):

    cdef public int _start
    cdef public int _stop
    cdef public Accumulator _valueHolder

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class CombinedValueHolder(Accumulator):

    cdef public Accumulator _left
    cdef public Accumulator _right

    cpdef push(self, dict data)
    cpdef bint isFull(self)


cdef class AddedValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class MinusedValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class MultipliedValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class DividedValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class LtOperatorValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class LeOperatorValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class GtOperatorValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class GeOperatorValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class EqOperatorValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class NeOperatorValueHolder(CombinedValueHolder):

    cpdef object result(self)


cdef class Identity(Accumulator):

    cdef public object _value

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class Latest(StatelessSingleValueAccumulator):

    cdef public object _latest

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class CompoundedValueHolder(Accumulator):

    cdef public Accumulator _left
    cdef public Accumulator _right

    cpdef push(self, dict data)
    cpdef bint isFull(self)
    cpdef object result(self)


cdef class IIF(Accumulator):

    cdef public Accumulator _cond
    cdef public Accumulator _left
    cdef public Accumulator _right

    cpdef push(self, dict data)
    cpdef object result(self)


cdef class BasicFunction(Accumulator):

    cdef public double _origValue

    cpdef push(self, dict data)


cdef class Exp(BasicFunction):

    cpdef object result(self)


cdef class Log(BasicFunction):

    cpdef object result(self)


cdef class Sqrt(BasicFunction):

    cpdef object result(self)


cdef class Pow(BasicFunction):

    cdef public double _n

    cpdef object result(self)


cdef class Abs(BasicFunction):

    cpdef object result(self)


cdef class Sign(BasicFunction):

    cpdef object result(self)


cdef class Acos(BasicFunction):

    cpdef object result(self)


cdef class Acosh(BasicFunction):

    cpdef object result(self)


cdef class Asin(BasicFunction):

    cpdef object result(self)


cdef class Asinh(BasicFunction):

    cpdef object result(self)