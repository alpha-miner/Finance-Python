# -*- coding: utf-8 -*-
u"""
Created on 2015-2-8

@author: cheng.li
"""

import operator
from copy import deepcopy
import math
import sys
import numpy as np
import pandas as pd
from PyFin.Utilities import pyFinAssert

# get the correct attribute of div
if sys.version_info > (3, 0, 0):
    div_attr = "truediv"
else:
    div_attr = "div"


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
        return NegativeValueHolder(self)

    def __getitem__(self, item):
        return TruncatedValueHolder(self, item)


cdef class Accumulator(IAccumulator):

    cdef public int _isFull
    cdef public object _dependency
    cdef public int _isValueHolderContained
    cdef public int _window
    cdef public int _returnSize

    def __init__(self, dependency):
        self._isFull = 0
        self._window = 0
        self._returnSize = 1

        if isinstance(dependency, Accumulator):
            self._isValueHolderContained = 1
        else:
            self._isValueHolderContained = 0
        if hasattr(dependency, '__iter__') and len(dependency) >= 2:
            for name in dependency:
                pyFinAssert(isinstance(name, str), ValueError, '{0} in pNames should be a plain string. But it is {1}'
                         .format(name,type(name)))
            self._dependency = dependency
        elif hasattr(dependency, '__iter__') and len(dependency) == 1:
            for name in dependency:
                pyFinAssert(isinstance(name, str), ValueError, '{0} in pNames should be a plain string. But it is {1}'
                         .format(name,type(name)))
            self._dependency = dependency[0]
        elif hasattr(dependency, '__iter__'):
            raise ValueError("parameters' name list should not be empty")
        else:
            pyFinAssert(isinstance(dependency, str) or isinstance(dependency, Accumulator), ValueError,
                        '{0} in pNames should be a plain string or an value holder. But it is {1}'
                        .format(dependency, type(dependency)))
            self._dependency = deepcopy(dependency)

    def extract(self, data):
        if not self._isValueHolderContained:
            try:
                return data[self._dependency]
            except (TypeError, KeyError) as _:
                try:
                    return tuple(data[p] for p in self._dependency)
                except KeyError:
                    return np.nan
        else:
            self._dependency.push(data)
            return self._dependency.result()

    def transform(self, data, name=None):
        data.sort_index()

        if not name:
            name = 'transformed'

        matrix_values = data.as_matrix()
        columns = data.columns.tolist()

        output_values = np.zeros(len(data))

        for i, row in enumerate(matrix_values):
            self.push({k: v for k, v in zip(columns, row)})
            output_values[i] = self.result()

        df = pd.Series(output_values, index=data.index, name=name)
        return df

    @property
    def value(self):
        return self.result()

    @property
    def isFull(self):
        return self._isFull == 1

    @property
    def window(self):
        return self._window

    @property
    def valueSize(self):
        return self._returnSize

    @property
    def dependency(self):
        if isinstance(self._dependency, str) or hasattr(self._dependency, '__iter__'):
            return self._dependency
        else:
            return self._dependency.dependency

    def __deepcopy__(self, memo):
        return Accumulator(self._dependency)


cdef class NegativeValueHolder(Accumulator):

    cdef public object _valueHolder

    def __init__(self, valueHolder):
        self._valueHolder = build_holder(valueHolder)
        self._returnSize = valueHolder.valueSize
        self._window = valueHolder.window
        self._dependency = deepcopy(valueHolder.dependency)
        self._isFull = 0

    def push(self, data):
        self._valueHolder.push(data)
        if self._valueHolder.isFull:
            self._isFull = 1

    def result(self):
        res = self._valueHolder.result()
        try:
            return -res
        except TypeError:
            return [-r for r in res]

    def __deepcopy__(self, memo):
        return NegativeValueHolder(self._valueHolder)


cdef class ListedValueHolder(Accumulator):

    cdef public object _left
    cdef public object _right

    def __init__(self, left, right):
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._returnSize = self._left.valueSize + self._right.valueSize
        self._dependency = list(set(self._left.dependency).union(set(self._right.dependency)))
        self._window = max(self._left.window, self._right.window)
        self._isFull = 0

    def push(self, data):
        self._left.push(data)
        self._right.push(data)
        if self._isFull == 0 and self._left.isFull and self._right.isFull:
            self._isFull = 1

    def result(self):
        resLeft = self._left.result()
        resRight = self._right.result()

        if not hasattr(resLeft, '__iter__'):
            resLeft = np.array([resLeft])
        if not hasattr(resRight, '__iter__'):
            resRight = np.array([resRight])
        return np.concatenate([resLeft, resRight])

    def __deepcopy__(self, memo):
        return ListedValueHolder(self._left, self._right)


cdef class TruncatedValueHolder(Accumulator):

    cdef public int _start
    cdef public int _stop
    cdef public object _valueHolder

    def __init__(self, valueHolder, item):
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

        self._valueHolder = build_holder(valueHolder)
        self._dependency = self._valueHolder.dependency
        self._window = valueHolder.window
        self._isFull = 0

    def push(self, data):
        self._valueHolder.push(data)
        if self._valueHolder.isFull:
            self._isFull = 1

    def result(self):
        if self._stop == -1:
            return self._valueHolder.result()[self._start]
        return self._valueHolder.result()[self._start:self._stop]

    def __deepcopy__(self, memo):
        if self._stop == -1:
            item = self._start
        else:
            item = slice(self._start, self._stop)
        return TruncatedValueHolder(self._valueHolder, item)


cdef class CombinedValueHolder(Accumulator):

    cdef public object _left
    cdef public object _right

    def __init__(self, left, right):
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._returnSize = self._left.valueSize
        self._dependency = list(set(self._left.dependency).union(set(self._right.dependency)))
        self._window = max(self._left.window, self._right.window)
        self._isFull = 0

    def push(self, data):
        self._left.push(data)
        self._right.push(data)
        if self._isFull == 0 and self._left.isFull and self._right.isFull:
            self._isFull = 1

    def __deepcopy__(self, memo):
        return CombinedValueHolder(self._left, self._right)


cdef class ArithmeticValueHolder(CombinedValueHolder):

    cdef public object _op

    def __init__(self, left, right, op):
        super(ArithmeticValueHolder, self).__init__(left, right)
        self._op = op

    def result(self):
        res1 = self._left.result()
        res2 = self._right.result()

        return self._op(res1, res2)

    @property
    def isFull(self):
        if self._left.isFull and self._right.isFull:
            return True
        else:
            return False

    def __deepcopy__(self, memo):
        return ArithmeticValueHolder(self._left, self._right, self._op)


cdef class AddedValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(AddedValueHolder, self).__init__(left, right, operator.add)

    def __deepcopy__(self, memo):
        return AddedValueHolder(self._left, self._right)


cdef class MinusedValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(MinusedValueHolder, self).__init__(left, right, operator.sub)

    def __deepcopy__(self, memo):
        return MinusedValueHolder(self._left, self._right)


cdef class MultipliedValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(MultipliedValueHolder, self).__init__(left, right, operator.mul)

    def __deepcopy__(self, memo):
        return MultipliedValueHolder(self._left, self._right)


cdef class DividedValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(DividedValueHolder, self).__init__(left, right, getattr(operator, div_attr))

    def __deepcopy__(self, memo):
        return DividedValueHolder(self._left, self._right)


cdef class LtOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(LtOperatorValueHolder, self).__init__(left, right, operator.lt)

    def __deepcopy__(self, memo):
        return LtOperatorValueHolder(self._left, self._right)


cdef class LeOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(LeOperatorValueHolder, self).__init__(left, right, operator.le)

    def __deepcopy__(self, memo):
        return LeOperatorValueHolder(self._left, self._right)


cdef class GtOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(GtOperatorValueHolder, self).__init__(left, right, operator.gt)

    def __deepcopy__(self, memo):
        return GtOperatorValueHolder(self._left, self._right)


cdef class GeOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(GeOperatorValueHolder, self).__init__(left, right, operator.ge)

    def __deepcopy__(self, memo):
        return GeOperatorValueHolder(self._left, self._right)


class EqOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(EqOperatorValueHolder, self).__init__(left, right, operator.eq)

    def __deepcopy__(self, memo):
        return EqOperatorValueHolder(self._left, self._right)


cdef class NeOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(NeOperatorValueHolder, self).__init__(left, right, operator.ne)

    def __deepcopy__(self, memo):
        return NeOperatorValueHolder(self._left, self._right)


cdef class Identity(Accumulator):

    cdef public double _value

    def __init__(self, value):
        self._dependency = []
        self._window = 0
        self._value = value
        self._returnSize = 1
        self._isFull = 0

    def push(self, data):
        pass

    def result(self):
        return self._value

    def __deepcopy__(self, memo):
        return Identity(self._value)


cdef class StatelessSingleValueAccumulator(Accumulator):

    def __init__(self, dependency='x'):
        super(StatelessSingleValueAccumulator, self).__init__(dependency)
        self._returnSize = 1
        self._window = 0

    def _push(self, data):
        if not self._isValueHolderContained:
            try:
                value = data[self._dependency]
            except KeyError:
                value = np.nan
        else:
            self._dependency.push(data)
            value = self._dependency.result()
        return value

    def __deepcopy__(self, memo):
        return StatelessSingleValueAccumulator(self._dependency)


cdef class Latest(StatelessSingleValueAccumulator):

    cdef public double _latest

    def __init__(self, dependency='x'):
        super(Latest, self).__init__(dependency)
        self._window = 0
        self._returnSize = 1
        self._latest = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        self._isFull = 1
        self._latest = value

    def result(self):
        return self._latest

    def __deepcopy__(self, memo):
        return Latest(self._dependency)


cdef int isanumber(a):
    cdef int bool_a = 1
    try:
        float(repr(a))
    except:
        bool_a = 0

    return bool_a


cpdef build_holder(name):
    if isinstance(name, Accumulator):
        return deepcopy(name)
    elif isinstance(name, str):
        return Latest(name)
    elif isanumber(name):
        return Identity(float(name))
    elif hasattr(name, '__iter__'):
        return build_holder(name[0])


cdef class CompoundedValueHolder(Accumulator):

    cdef public object _left
    cdef public object _right

    def __init__(self, left, right):
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

    def push(self, data):
        self._left.push(data)
        values = self._left.result()
        if not hasattr(values, '__iter__'):
            parameters = {self._right.dependency: values}
        else:
            parameters = dict((name, value) for name, value in zip(self._right.dependency, values))
        self._right.push(parameters)

    def result(self):
        return self._right.result()

    @property
    def isFull(self):
        if self._left.isFull and self._right.isFull:
            return True
        else:
            return False

    def __deepcopy__(self, memo):
        return CompoundedValueHolder(self._left, self._right)


cdef class IIF(Accumulator):

    cdef public object _cond
    cdef public object _left
    cdef public object _right

    def __init__(self, cond, left, right):
        self._cond = build_holder(cond)
        self._returnSize = self._cond.valueSize
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._dependency = list(set(self._cond.dependency).union(set(self._cond.dependency).union(set(self._cond.dependency))))
        self._window = max(self._cond.window, self._left.window, self._right.window)
        self._isFull = 0

    def push(self, data):
        self._cond.push(data)
        self._left.push(data)
        self._right.push(data)
        if self._isFull == 0 and self._cond.isFull and self._left.isFull and self._right.isFull:
            self._isFull = 1

    def result(self):
        return self._left.result() if self._cond.result() else self._right.result()

    def __deepcopy__(self, memo):
        return IIF(self._cond, self._left, self._right)


cdef class BasicFunction(Accumulator):

    cdef public object _origValue
    cdef public object _func

    def __init__(self, dependency, func):
        super(BasicFunction, self).__init__(dependency)
        if self._isValueHolderContained:
            self._returnSize = self._dependency.valueSize
            self._window = self._dependency.window
        else:
            self._returnSize = 1
            self._window = 1
        self._func = func
        self._isFull = 0
        self._origValue = np.nan

    def push(self, data):
        value = self.extract(data)
        if self._returnSize == 1:
            if math.isnan(value):
                return np.nan
        else:
            if np.any(np.isnan(value)):
                return np.nan
        self._origValue = value
        self._isFull = 1

    def result(self):
        try:
            return self._func(self._origValue)
        except ValueError:
            return np.nan
        except TypeError:
            return np.array([self._func(v) for v in self._origValue])

    def __deepcopy__(self, memo):
        return BasicFunction(self._dependency, self._func)


cdef class Exp(BasicFunction):
    def __init__(self, dependency):
        super(Exp, self).__init__(dependency, math.exp)

    def __deepcopy__(self, memo):
        return Exp(self._dependency)


cdef class Log(BasicFunction):
    def __init__(self, dependency):
        super(Log, self).__init__(dependency, math.log)

    def __deepcopy__(self, memo):
        return Log(self._dependency)


cdef class Sqrt(BasicFunction):
    def __init__(self, dependency):
        super(Sqrt, self).__init__(dependency, math.sqrt)

    def __deepcopy__(self, memo):
        return Sqrt(self._dependency)


# due to the fact that pow function is much slower than ** operator
cdef class Pow(Accumulator):

    cdef public object _origValue
    cdef public double _n

    def __init__(self, dependency, n):
        super(Pow, self).__init__(dependency)
        if self._isValueHolderContained:
            self._returnSize = self._dependency.valueSize
            self._window = self._dependency.window
        else:
            self._returnSize = 1
            self._window = 1
        self._isFull = 0
        self._origValue = np.nan
        self._n = n

    def push(self, data):
        value = self.extract(data)
        if self._returnSize == 1:
            if math.isnan(value):
                return np.nan
        else:
            if np.any(np.isnan(value)):
                return np.nan
        self._origValue = value
        self._isFull = 1

    def result(self):

        try:
            return self._origValue ** self._n
        except TypeError:
            return np.array(v ** self._n for v in self._origValue)

    def __deepcopy__(self, memo):
        return Pow(self._dependency, self._n)


cdef class Abs(BasicFunction):
    def __init__(self, dependency):
        super(Abs, self).__init__(dependency, abs)

    def __deepcopy__(self, memo):
        return Abs(self._dependency)


cdef double sign(double x):
    if x > 0.:
        return 1.
    elif x < 0.:
        return -1.
    else:
        return 0.


cdef class Sign(BasicFunction):
    def __init__(self, dependency):
        super(Sign, self).__init__(dependency, sign)

    def __deepcopy__(self, memo):
        return Sign(self._dependency)


cdef class Acos(BasicFunction):
    def __init__(self, dependency):
        super(Acos, self).__init__(dependency, math.acos)

    def __deepcopy__(self, memo):
        return Acos(self._dependency)


cdef class Acosh(BasicFunction):
    def __init__(self, dependency):
        super(Acosh, self).__init__(dependency, math.acosh)

    def __deepcopy__(self, memo):
        return Acosh(self._dependency)


cdef class Asin(BasicFunction):
    def __init__(self, dependency):
        super(Asin, self).__init__(dependency, math.asin)

    def __deepcopy__(self, memo):
        return Asin(self._dependency)


cdef class Asinh(BasicFunction):
    def __init__(self, dependency):
        super(Asinh, self).__init__(dependency, math.asinh)

    def __deepcopy__(self, memo):
        return Asinh(self._dependency)
