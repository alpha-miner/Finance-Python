# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""

import copy
from copy import deepcopy
import six
from libc.math cimport sqrt
from libc.math cimport fabs
from libc.math cimport log
from libc.math cimport exp
from libc.math cimport acos
from libc.math cimport acosh
from libc.math cimport asin
from libc.math cimport asinh
cimport cython
import numpy as np
cimport numpy as np
import pandas as pd
from PyFin.Utilities.Asserts cimport pyFinAssert
from PyFin.Math.MathConstants cimport NAN
from PyFin.Math.udfs cimport sign


cdef class IAccumulator(object):

    def __add__(self, right):
        return AddedValueHolder(self, right)

    def __sub__(self, right):
        return MinusedValueHolder(self, right)

    def __mul__(self, right):
        return MultipliedValueHolder(self, right)

    def __div__(self, right):
        return DividedValueHolder(self, right)

    # only work for python 3
    def __truediv__(self, right):
        return DividedValueHolder(self, right)

    def __richcmp__(self, right, int op):
        if op == 0:
            return LtOperatorValueHolder(self, right)
        elif op == 1:
            return LeOperatorValueHolder(self, right)
        elif op == 2:
            return EqOperatorValueHolder(self, right)
        elif op == 3:
            return NeOperatorValueHolder(self, right)
        elif op == 4:
            return GtOperatorValueHolder(self, right)
        elif op == 5:
            return GeOperatorValueHolder(self, right)

    def __rshift__(self, right):
        if isinstance(right, IAccumulator):
            return CompoundedValueHolder(self, right)

        try:
            return right(self)
        except TypeError:
            raise ValueError('{0} is not recognized as a valid operator'.format(right))

    def __neg__(self):
        return Negative(self)


cdef class Accumulator(IAccumulator):

    def __init__(self, dependency):
        self._isFull = False
        self._window = 0
        self._returnSize = 1

        if isinstance(dependency, Accumulator):
            self._isValueHolderContained = True
            self._dependency = deepcopy(dependency)
            self._isStringDependency = False
        else:
            self._isValueHolderContained = False
            if (isinstance(dependency, tuple) or isinstance(dependency, list)) and len(dependency) > 1:
                self._dependency = dependency
                self._isStringDependency=False
            elif (isinstance(dependency, tuple) or isinstance(dependency, list)) and len(dependency) == 1:
                self._dependency = dependency[0]
                self._isStringDependency = True
            else:
                self._dependency = dependency
                self._isStringDependency = True


    cdef extract(self, dict data):
        cdef str p
        cdef Accumulator comp

        if not self._isValueHolderContained:
            if self._isStringDependency:
                try:
                    return data[self._dependency]
                except KeyError:
                    return NAN
            else:
                try:
                    return tuple(data[p] for p in self._dependency)
                except KeyError:
                    return NAN
        else:
            comp = self._dependency
            comp.push(data)
            return comp.result()

    cpdef push(self, dict data):
        pass

    cpdef object result(self):
        pass

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef transform(self, data, str name=None, bint to_sort=False):

        cdef int i
        cdef int k
        cdef double[:, :] matrix_values
        cdef size_t n = len(data)
        cdef double[:] output_values = np.zeros(n)
        cdef list columns
        cdef size_t column_length
        cdef dict data_dict

        if to_sort:
            data.sort_index(inplace=True)

        if not name:
            name = 'transformed'

        data = data.select_dtypes([np.number])
        matrix_values = data.as_matrix().astype(float)
        columns = data.columns.tolist()
        column_length = len(columns)

        data_dict = {columns[k]: 0 for k in range(column_length)}

        for i in range(n):
            for k in range(column_length):
                data_dict[columns[k]] = matrix_values[i, k]
            self.push(data_dict)
            output_values[i] = self.result()

        return pd.Series(output_values, index=data.index, name=name)

    @property
    def value(self):
        return self.result()

    cpdef bint isFull(self):
        return self._isFull

    @property
    def window(self):
        return self._window

    @property
    def valueSize(self):
        return self._returnSize

    @property
    def dependency(self):
        if isinstance(self._dependency, six.string_types) or hasattr(self._dependency, '__iter__'):
            return self._dependency
        else:
            return self._dependency.dependency

    cpdef copy_attributes(self, dict attributes, bint is_deep=True):
        self._isFull = attributes['_isFull']
        self._dependency = copy.deepcopy(attributes['_dependency']) if is_deep else attributes['_dependency']
        self._isValueHolderContained = attributes['_isValueHolderContained']
        self._window = attributes['_window']
        self._returnSize = attributes['_returnSize']
        self._isStringDependency = attributes['_isStringDependency']

    cpdef collect_attributes(self):
        attributes = dict()
        attributes['_isFull'] = self._isFull
        attributes['_dependency'] = self._dependency
        attributes['_isValueHolderContained'] = self._isValueHolderContained
        attributes['_window'] = self._window
        attributes['_returnSize'] = self._returnSize
        attributes['_isStringDependency'] = self._isStringDependency
        return attributes


cdef class Negative(Accumulator):

    def __init__(self, valueHolder):
        super(Negative, self).__init__(valueHolder)
        self._returnSize = valueHolder.valueSize
        self._window = valueHolder.window
        self._isFull = False

    cpdef push(self, dict data):
        self._dependency.push(data)
        self._isFull = self._dependency.isFull()

    def __str__(self):
        return "-{0}".format(str(self._dependency))

    cpdef object result(self):
        cdef double res = self._dependency.result()
        return -res


cdef class CombinedValueHolder(Accumulator):

    def __init__(self, left, right):
        super(CombinedValueHolder, self).__init__([])
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._returnSize = self._left.valueSize
        self._dependency = list(set(self._left.dependency).union(set(self._right.dependency)))
        self._window = max(self._left.window, self._right.window)
        self._isFull = False

    cpdef push(self, dict data):
        self._left.push(data)
        self._right.push(data)
        self._isFull = self._isFull or (self._left.isFull() and self._right.isFull())

    cpdef bint isFull(self):
        return self._isFull


cdef class AddedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(AddedValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 + res2

    def __str__(self):
        return "{0} + {1}".format(str(self._left), str(self._right))


cdef class MinusedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(MinusedValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 - res2

    def __str__(self):
        return "{0} - {1}".format(str(self._left), str(self._right))


cdef class MultipliedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(MultipliedValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 * res2

    def __str__(self):

        if isinstance(self._left, (AddedValueHolder, MinusedValueHolder)):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  (AddedValueHolder, MinusedValueHolder)):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \\times {1}".format(s1, s2)


cdef class DividedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(DividedValueHolder, self).__init__(left, right)

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 / res2

    def __str__(self):
        return "\\frac{{{0}}}{{{1}}}".format(str(self._left), str(self._right))


cdef class LtOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(LtOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 < res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \lt {1}".format(s1, s2)


cdef class LeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(LeOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 <= res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \le {1}".format(s1, s2)


cdef class GtOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(GtOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 > res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \gt {1}".format(s1, s2)


cdef class GeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(GeOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 >= res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \ge {1}".format(s1, s2)


cdef class EqOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(EqOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 == res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} = {1}".format(s1, s2)


cdef class NeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(NeOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 != res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \\neq {1}".format(s1, s2)


cdef class Identity(Accumulator):

    def __init__(self, value):
        self._dependency = []
        self._window = 0
        self._value = value
        self._returnSize = 1
        self._isFull = True

    cpdef push(self, dict data):
        pass

    cpdef object result(self):
        return self._value

    def __str__(self):
        return str(self._value)


cdef class StatelessSingleValueAccumulator(Accumulator):

    def __init__(self, dependency='x'):
        super(StatelessSingleValueAccumulator, self).__init__(dependency)
        self._returnSize = 1
        self._window = 0

    cdef _push(self, dict data):

        cdef Accumulator comp

        if not self._isValueHolderContained:
            try:
                value = data[self._dependency]
            except KeyError:
                value = NAN
        else:
            comp = self._dependency
            comp.push(data)
            value = comp.result()
        return value


cdef class Latest(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x', current_value=NAN):
        super(Latest, self).__init__(dependency)
        self._window = 0
        self._returnSize = 1
        self._isFull = True
        self._latest = current_value

    cpdef push(self, dict data):
        self._latest = self._push(data)

    def __str__(self):
        if self._isValueHolderContained:
            return "{0}".format(str(self._dependency))
        else:
            return "''\\text{{{0}}}''".format(str(self._dependency))

    cpdef object result(self):
        return self._latest


cdef bint isanumber(a):
    cdef bint bool_a = True
    try:
        float(repr(a))
    except:
        bool_a = False

    return bool_a


cpdef build_holder(name):
    if isinstance(name, Accumulator):
        return deepcopy(name)
    elif isinstance(name, six.string_types):
        return Latest(name)
    elif isanumber(name):
        return Identity(float(name))
    elif hasattr(name, '__iter__'):
        return build_holder(name[0])


cdef class CompoundedValueHolder(Accumulator):

    def __init__(self, left, right):
        super(CompoundedValueHolder, self).__init__([])
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._returnSize = self._right.valueSize
        self._window = self._left.window + self._right.window - 1
        self._dependency = deepcopy(self._left.dependency)

        if hasattr(right.dependency, '__iter__'):
            pyFinAssert(left.valueSize == len(right.dependency), ValueError, "left value size {0} "
                                                                          "should be equal to right dependency size {1}"
                     .format(left.valueSize, len(right.dependency)))
        else:
            pyFinAssert(left.valueSize == 1, ValueError, "left value size {0} should be equal to right dependency size 1"
                     .format(left.valueSize))

    cpdef push(self, dict data):
        self._left.push(data)
        values = self._left.result()
        if not hasattr(values, '__iter__'):
            parameters = {self._right.dependency: values}
        else:
            parameters = {name: value for name, value in zip(self._right.dependency, values)}
        self._right.push(parameters)
        self._isFull = self._isFull or (self._left.isFull() and self._right.isFull())

    cpdef object result(self):
        return self._right.result()

    cpdef bint isFull(self):
        return self._isFull


cdef class IIF(Accumulator):

    def __init__(self, cond, left, right):
        super(IIF, self).__init__([])
        self._cond = build_holder(cond)
        self._returnSize = self._cond.valueSize
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._dependency = list(set(self._cond.dependency).union(set(self._cond.dependency).union(set(self._cond.dependency))))
        self._window = max(self._cond.window, self._left.window, self._right.window)
        self._isFull = False

    cpdef push(self, dict data):
        self._cond.push(data)
        self._left.push(data)
        self._right.push(data)
        self._isFull = self._isFull or (self._cond.isFull() and self._left.isFull() and self._right.isFull())

    cpdef object result(self):
        return self._left.result() if self._cond.result() else self._right.result()


cdef class BasicFunction(Accumulator):

    def __init__(self, dependency, orig_value=NAN):
        super(BasicFunction, self).__init__(dependency)
        if self._isValueHolderContained:
            self._window = self._dependency.window
        else:
            self._window = 1
        self._returnSize = 1
        self._isFull = 1
        self._origValue = orig_value

    cpdef push(self, dict data):

        cdef double value = self.extract(data)
        self._origValue = value


cdef class Exp(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Exp, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return exp(self._origValue)

    def __str__(self):
        if self._isValueHolderContained:
            return "\\exp({0})".format(str(self._dependency))
        else:
            return "\\exp(''\\text{{{0}}}'')".format(str(self._dependency))


cdef class Log(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Log, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return log(self._origValue)

    def __str__(self):
        if self._isValueHolderContained:
            return "\\ln({0})".format(str(self._dependency))
        else:
            return "\\ln(''\\text{{{0}}}'')".format(str(self._dependency))


cdef class Sqrt(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Sqrt, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return sqrt(self._origValue)

    def __str__(self):
        if self._isValueHolderContained:
            return "\\sqrt{{{0}}}".format(str(self._dependency))
        else:
            return "\\sqrt{{''\\text{{{0}}}''}}".format(str(self._dependency))


# due to the fact that pow function is much slower than ** operator
cdef class Pow(BasicFunction):

    def __init__(self, dependency, n, orig_value=NAN):
        super(Pow, self).__init__(dependency, orig_value)
        self._n = n

    cpdef object result(self):
        return self._origValue ** self._n

    def __str__(self):
        if self._isValueHolderContained:
            return "{0} ^ {{{1}}}".format(str(self._dependency), self._n)
        else:
            return "''\\text{{{0}}}'' ^ {{{1}}}".format(str(self._dependency), self._n)


cdef class Abs(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Abs, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return fabs(self._origValue)

    def __str__(self):
        if self._isValueHolderContained:
            return "\\left| {0} \\right|".format(str(self._dependency))
        else:
            return "\\left|  ''\\text{{{0}}}'' \\right|".format(str(self._dependency))


cdef class Sign(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Sign, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return sign(self._origValue)

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{sign}}({0})".format(str(self._dependency))
        else:
            return "\\mathrm{{sign}}(''\\text{{{0}}}'')".format(str(self._dependency))


cdef class Acos(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Acos, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return acos(self._origValue)

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{ACos}}({0})".format(str(self._dependency))
        else:
            return "\\mathrm{{ACos}}(''\\text{{{0}}}'')".format(str(self._dependency))


cdef class Acosh(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Acosh, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return acosh(self._origValue)

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{ACosh}}({0})".format(str(self._dependency))
        else:
            return "\\mathrm{{ACosh}}(''\\text{{{0}}}'')".format(str(self._dependency))


cdef class Asin(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Asin, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return asin(self._origValue)

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{ASin}}({0})".format(str(self._dependency))
        else:
            return "\\mathrm{{ASin}}(''\\text{{{0}}}'')".format(str(self._dependency))


cdef class Asinh(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Asinh, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return asinh(self._origValue)

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{ASinh}}({0})".format(str(self._dependency))
        else:
            return "\\mathrm{{ASinh}}(''\\text{{{0}}}'')".format(str(self._dependency))
