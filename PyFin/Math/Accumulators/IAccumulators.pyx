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
        elif op == 4:
            return GtOperatorValueHolder(self, right)
        elif op == 5:
            return GeOperatorValueHolder(self, right)

    def __xor__(self, right):
        return ListedValueHolder(self, right)

    def __rshift__(self, right):
        if isinstance(right, IAccumulator):
            return CompoundedValueHolder(self, right)

        try:
            return right(self)
        except TypeError:
            raise ValueError('{0} is not recognized as a valid operator'.format(right))

    def __neg__(self):
        return Negative(self)

    def __getitem__(self, item):
        return TruncatedValueHolder(self, item)


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

    def __deepcopy__(self, memo):
        return Accumulator(self._dependency)

    def __reduce__(self):
        d = {}

        return Accumulator, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Negative(Accumulator):

    def __init__(self, valueHolder):
        super(Negative, self).__init__(valueHolder)
        self._returnSize = valueHolder.valueSize
        self._window = valueHolder.window
        self._isFull = False

    cpdef push(self, dict data):
        self._dependency.push(data)
        self._isFull = self._dependency.isFull()

    cpdef object result(self):
        res = self._dependency.result()
        try:
            return -res
        except TypeError:
            return [-r for r in res]

    def __deepcopy__(self, memo):
        return Negative(self._valueHolder)

    def __reduce__(self):
        d = {}

        return Negative, (self._valueHolder, ), d

    def __setstate__(self, state):
        pass


cdef class ListedValueHolder(Accumulator):

    def __init__(self, left, right):
        super(ListedValueHolder, self).__init__([])
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._returnSize = self._left.valueSize + self._right.valueSize
        self._dependency = list(set(self._left.dependency).union(set(self._right.dependency)))
        self._window = max(self._left.window, self._right.window)
        self._isValueHolderContained = True
        self._isFull = False

    cpdef push(self, dict data):
        self._left.push(data)
        self._right.push(data)
        self._isFull =  self._isFull or (self._left.isFull() and self._right.isFull())

    cpdef object result(self):
        resLeft = self._left.result()
        resRight = self._right.result()

        if not hasattr(resLeft, '__iter__'):
            resLeft = np.array([resLeft])
        if not hasattr(resRight, '__iter__'):
            resRight = np.array([resRight])
        return np.concatenate([resLeft, resRight])

    def __deepcopy__(self, memo):
        return ListedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return ListedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class TruncatedValueHolder(Accumulator):

    def __init__(self, valueHolder, item):
        super(TruncatedValueHolder, self).__init__(valueHolder)
        if valueHolder.valueSize == 1:
            raise TypeError("scalar valued holder ({0}) can't be sliced".format(valueHolder))
        if isinstance(item, slice):
            self._start = item.start
            self._stop = item.stop
            length = item.stop - item.start
            if length < 0:
                length += valueHolder.valueSize
            if length < 0:
                raise ValueError('start {0:d} and end {0:d} are not compatible'.format(item.start, item.stop))
            self._returnSize = length
        else:
            self._start = item
            self._stop = -1
            self._returnSize = 1
        self._window = valueHolder.window
        self._isFull = 0

    cpdef push(self, dict data):
        self._dependency.push(data)
        self._isFull = self._dependency.isFull()

    cpdef object result(self):
        if self._stop == -1:
            return self._dependency.result()[self._start]
        return self._dependency.result()[self._start:self._stop]

    def __deepcopy__(self, memo):
        if self._stop == -1:
            item = self._start
        else:
            item = slice(self._start, self._stop)
        return TruncatedValueHolder(self._dependency, item)

    def __reduce__(self):
        d = {}

        if self._stop == -1:
            item = self._start
        else:
            item = slice(self._start, self._stop)

        return TruncatedValueHolder, (self._dependency, item), d

    def __setstate__(self, state):
        pass


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

    def __deepcopy__(self, memo):
        return CombinedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return CombinedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class AddedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(AddedValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 + res2

    def __deepcopy__(self, memo):
        return AddedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return AddedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class MinusedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(MinusedValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 - res2

    def __deepcopy__(self, memo):
        return MinusedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return MinusedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class MultipliedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(MultipliedValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 * res2

    def __deepcopy__(self, memo):
        return MultipliedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return MultipliedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class DividedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(DividedValueHolder, self).__init__(left, right)

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 / res2

    def __deepcopy__(self, memo):
        return DividedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return DividedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class LtOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(LtOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 < res2

    def __deepcopy__(self, memo):
        return LtOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return LtOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class LeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(LeOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 <= res2

    def __deepcopy__(self, memo):
        return LeOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return LeOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class GtOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(GtOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 > res2

    def __deepcopy__(self, memo):
        return GtOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return GtOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class GeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(GeOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 >= res2

    def __deepcopy__(self, memo):
        return GeOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return GeOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class EqOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(EqOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 == res2

    def __deepcopy__(self, memo):
        return EqOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return EqOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class NeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(NeOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 != res2

    def __deepcopy__(self, memo):
        return NeOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return NeOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


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

    def __deepcopy__(self, memo):
        return Identity(self._value)

    def __reduce__(self):
        d = {}

        return Identity, (self._value,), d

    def __setstate__(self, state):
        pass


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

    def __deepcopy__(self, memo):
        return StatelessSingleValueAccumulator(self._dependency)

    def __reduce__(self):
        d = {}

        return StatelessSingleValueAccumulator, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Latest(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x', current_value=NAN):
        super(Latest, self).__init__(dependency)
        self._window = 0
        self._returnSize = 1
        self._isFull = True
        self._latest = current_value

    cpdef push(self, dict data):
        self._latest = self._push(data)

    cpdef object result(self):
        return self._latest

    def __deepcopy__(self, memo):
        return Latest(self._dependency, self._latest)

    def __reduce__(self):
        d = {}

        return Latest, (self._dependency, self._latest), d

    def __setstate__(self, state):
        pass

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

    def __deepcopy__(self, memo):
        return CompoundedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return CompoundedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


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

    def __deepcopy__(self, memo):
        return IIF(self._cond, self._left, self._right)

    def __reduce__(self):
        d = {}

        return IIF, (self._cond, self._left, self._right), d

    def __setstate__(self, state):
        pass


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

    def __deepcopy__(self, memo):
        return BasicFunction(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return BasicFunction, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass


cdef class Exp(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Exp, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return exp(self._origValue)

    def __deepcopy__(self, memo):
        return Exp(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return Exp, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass


cdef class Log(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Log, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return log(self._origValue)

    def __deepcopy__(self, memo):
        return Log(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return Log, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass


cdef class Sqrt(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Sqrt, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return sqrt(self._origValue)

    def __deepcopy__(self, memo):
        return Sqrt(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return Sqrt, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass


# due to the fact that pow function is much slower than ** operator
cdef class Pow(BasicFunction):

    def __init__(self, dependency, n, orig_value=NAN):
        super(Pow, self).__init__(dependency, orig_value)
        self._n = n

    cpdef object result(self):
        return self._origValue ** self._n

    def __deepcopy__(self, memo):
        return Pow(self._dependency, self._n, self._origValue)

    def __reduce__(self):
        d = {}

        return Pow, (self._dependency, self._n, self._origValue), d

    def __setstate__(self, state):
        pass


cdef class Abs(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Abs, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return fabs(self._origValue)

    def __deepcopy__(self, memo):
        return Abs(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return Abs, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass


cdef class Sign(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Sign, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return sign(self._origValue)

    def __deepcopy__(self, memo):
        return Sign(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return Sign, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass


cdef class Acos(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Acos, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return acos(self._origValue)

    def __deepcopy__(self, memo):
        return Acos(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return Acos, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass


cdef class Acosh(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Acosh, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return acosh(self._origValue)

    def __deepcopy__(self, memo):
        return Acosh(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return Acosh, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass


cdef class Asin(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Asin, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return asin(self._origValue)

    def __deepcopy__(self, memo):
        return Asin(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return Asin, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass


cdef class Asinh(BasicFunction):
    def __init__(self, dependency, orig_value=NAN):
        super(Asinh, self).__init__(dependency, orig_value)

    cpdef object result(self):
        return asinh(self._origValue)

    def __deepcopy__(self, memo):
        return Asinh(self._dependency, self._origValue)

    def __reduce__(self):
        d = {}

        return Asinh, (self._dependency, self._origValue), d

    def __setstate__(self, state):
        pass
