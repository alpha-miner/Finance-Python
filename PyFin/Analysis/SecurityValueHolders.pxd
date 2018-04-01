# -*- coding: utf-8 -*-
u"""
Created on 2017-2-11

@author: cheng.li
"""

from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Analysis.SeriesValues cimport SeriesValues


cdef class SecurityValueHolder(object):

    cdef public list _dependency
    cdef public SecurityValueHolder _compHolder
    cdef public int _window
    cdef public Accumulator _holderTemplate
    cdef public int updated
    cdef public dict _innerHolders
    cdef public SeriesValues cached

    cpdef push(self, dict data)
    cpdef value_all(self)
    cpdef SeriesValues value_by_names(self, list names)
    cpdef double value_by_name(self, name)
    cpdef shift(self, int n)
    cpdef transform(self, data, str name=*, str category_field=*, bint dropna=*)


cdef class FilteredSecurityValueHolder(SecurityValueHolder):

    cdef public SecurityValueHolder _filter
    cdef public SecurityValueHolder _computer

    cpdef double value_by_name(self, name)
    cpdef SeriesValues value_by_names(self, list names)
    cpdef push(self, dict data)


cdef class IdentitySecurityValueHolder(SecurityValueHolder):

    cdef public object _value
    cdef set _symbols

    cpdef push(self, dict data)
    cpdef double value_by_name(self, name)
    cpdef SeriesValues value_all(self)
    cpdef SeriesValues value_by_names(self, list names)


cdef class SecurityConstArrayValueHolder(SecurityValueHolder):
    cdef SeriesValues _values

    cpdef push(self, dict data)
    cpdef double value_by_name(self, name)
    cpdef SeriesValues value_all(self)
    cpdef SeriesValues value_by_names(self, list names)


cdef class SecurityUnitoryValueHolder(SecurityValueHolder):

    cdef public SecurityValueHolder _right
    cdef public object _op

    cpdef double value_by_name(self, name)
    cpdef SeriesValues value_all(self)
    cpdef SeriesValues value_by_names(self, list names)
    cpdef push(self, dict data)


cdef class SecurityNegValueHolder(SecurityUnitoryValueHolder):
    pass


cdef class SecurityInvertValueHolder(SecurityUnitoryValueHolder):
    pass


cdef class SecurityLatestValueHolder(SecurityValueHolder):
    cdef dict _symbol_values

    cpdef push(self, dict data)
    cpdef SeriesValues value_all(self)
    cpdef SeriesValues value_by_names(self, list names)
    cpdef double value_by_name(self, name)


cpdef SecurityValueHolder build_holder(name)


cdef class SecurityCombinedValueHolder(SecurityValueHolder):

    cdef public SecurityValueHolder _left
    cdef public SecurityValueHolder _right
    cdef public object _op

    cpdef double value_by_name(self, name)
    cpdef SeriesValues value_all(self)
    cpdef SeriesValues value_by_names(self, list names)
    cpdef push(self, dict data)

cdef class SecurityXorValueHolder(SecurityCombinedValueHolder):

    cpdef double value_by_name(self, name)


cdef class SecurityAddedValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecuritySubbedValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityMultipliedValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityDividedValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityLtOperatorValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityLeOperatorValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityGtOperatorValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityGeOperatorValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityEqOperatorValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityNeOperatorValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityAndOperatorValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityOrOperatorValueHolder(SecurityCombinedValueHolder):
    pass


cdef class SecurityShiftedValueHolder(SecurityValueHolder):
    pass


cdef class SecurityIIFValueHolder(SecurityValueHolder):

    cdef public SecurityValueHolder _flag
    cdef public SecurityValueHolder _left
    cdef public SecurityValueHolder _right

    cpdef double value_by_name(self, name)
    cpdef SeriesValues value_all(self)
    cpdef SeriesValues value_by_names(self, list names)
    cpdef push(self, dict data)