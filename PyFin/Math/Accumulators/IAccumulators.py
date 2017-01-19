# -*- coding: utf-8 -*-
u"""
Created on 2015-7-26

@author: cheng.li
"""

from abc import ABCMeta
from abc import abstractmethod
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


class Accumulator(object):

    def __init__(self, dependency):
        self._isFull = 0
        if isinstance(dependency, Accumulator):
            self._isValueHolderContained = True
        else:
            self._isValueHolderContained = False
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

    def push(self, data):
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

    @abstractmethod
    def result(self):
        raise NotImplementedError("result method is not implemented for Accumulator interface class")

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

    def _binary_operator(self, right, operatorHolder):
        if isinstance(right, Accumulator):
            return operatorHolder(self, right)
        return operatorHolder(self, Identity(right))

    def __add__(self, right):
        return self._binary_operator(right, AddedValueHolder)

    def __radd__(self, left):
        return AddedValueHolder(self, Identity(left))

    def __sub__(self, right):
        return self._binary_operator(right, MinusedValueHolder)

    def __rsub__(self, left):
        return MinusedValueHolder(Identity(left), self)

    def __mul__(self, right):
        return self._binary_operator(right, MultipliedValueHolder)

    def __rmul__(self, left):
        return MultipliedValueHolder(self, Identity(left))

    def __div__(self, right):
        return self._binary_operator(right, DividedValueHolder)

    def __rdiv__(self, left):
        return DividedValueHolder(Identity(left), self)

    # only work for python 3
    def __truediv__(self, right):
        return self.__div__(right)

    # only work for python 3
    def __rtruediv__(self, left):
        return self.__rdiv__(left)

    def __le__(self, right):
        return self._binary_operator(right, LeOperatorValueHolder)

    def __lt__(self, right):
        return self._binary_operator(right, LtOperatorValueHolder)

    def __ge__(self, right):
        return self._binary_operator(right, GeOperatorValueHolder)

    def __gt__(self, right):
        return self._binary_operator(right, GtOperatorValueHolder)

    def __xor__(self, right):
        if isinstance(right, Accumulator):
            return ListedValueHolder(self, right)
        return ListedValueHolder(self, Identity(right))

    def __rxor__(self, left):
        return ListedValueHolder(Identity(left), self)

    def __rshift__(self, right):
        if isinstance(right, Accumulator):
            return CompoundedValueHolder(self, right)

        try:
            return right(self)
        except TypeError:
            raise ValueError('{0} is not recognized as a valid operator'.format(right))

    def __neg__(self):
        return NegativeValueHolder(self)

    def __getitem__(self, item):
        return TruncatedValueHolder(self, item)


class NegativeValueHolder(Accumulator):
    def __init__(self, valueHolder):
        self._valueHolder = build_holder(valueHolder)
        self._returnSize = valueHolder.valueSize
        self._window = valueHolder.window
        self._containerSize = valueHolder._containerSize
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


class ListedValueHolder(Accumulator):
    def __init__(self, left, right):
        self._returnSize = left.valueSize + right.valueSize
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._dependency = list(set(left.dependency).union(set(right.dependency)))
        self._window = max(self._left.window, self._right.window)
        self._containerSize = max(self._left._containerSize, self._right._containerSize)
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


class TruncatedValueHolder(Accumulator):
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
            self._stop = None
            self._returnSize = 1

        self._valueHolder = build_holder(valueHolder)
        self._dependency = self._valueHolder.dependency
        self._window = valueHolder.window
        self._containerSize = valueHolder._containerSize
        self._isFull = 0

    def push(self, data):
        self._valueHolder.push(data)
        if self._valueHolder.isFull:
            self._isFull = 1

    def result(self):
        if self._stop is None:
            return self._valueHolder.result()[self._start]
        return self._valueHolder.result()[self._start:self._stop]


class CombinedValueHolder(Accumulator):
    def __init__(self, left, right):
        self._returnSize = left.valueSize
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._dependency = list(set(left.dependency).union(set(right.dependency)))
        self._window = max(self._left.window, self._right.window)
        self._containerSize = max(self._left._containerSize, self._right._containerSize)
        self._isFull = 0

    def push(self, data):
        self._left.push(data)
        self._right.push(data)
        if self._isFull == 0 and self._left.isFull and self._right.isFull:
            self._isFull = 1


class ArithmeticValueHolder(CombinedValueHolder):
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


class AddedValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(AddedValueHolder, self).__init__(left, right, operator.add)


class MinusedValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(MinusedValueHolder, self).__init__(left, right, operator.sub)


class MultipliedValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(MultipliedValueHolder, self).__init__(left, right, operator.mul)


class DividedValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(DividedValueHolder, self).__init__(left, right, getattr(operator, div_attr))


class LtOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(LtOperatorValueHolder, self).__init__(left, right, operator.lt)


class LeOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(LeOperatorValueHolder, self).__init__(left, right, operator.le)


class GtOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(GtOperatorValueHolder, self).__init__(left, right, operator.gt)


class GeOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(GeOperatorValueHolder, self).__init__(left, right, operator.ge)


class EqOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(EqOperatorValueHolder, self).__init__(left, right, operator.eq)


class NeOperatorValueHolder(ArithmeticValueHolder):
    def __init__(self, left, right):
        super(NeOperatorValueHolder, self).__init__(left, right, operator.ne)


class Identity(Accumulator):
    def __init__(self, value):
        self._dependency = []
        self._isValueHolder = False
        self._window = 0
        self._containerSize = 1
        self._value = value
        self._returnSize = 1
        self._isFull = 0

    def push(self, data):
        pass

    def result(self):
        return self._value


class StatelessSingleValueAccumulator(Accumulator):
    def __init__(self, dependency='x'):
        super(StatelessSingleValueAccumulator, self).__init__(dependency)
        self._returnSize = 1
        self._window = 1
        self._containerSize = 1

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


class Latest(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Latest, self).__init__(dependency)
        self._window = 1
        self._returnSize = 1
        self._containerSize = 1
        self._latest = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        self._isFull = 1
        self._latest = value

    def result(self):
        return self._latest


def build_holder(name):
    if isinstance(name, Accumulator):
        return deepcopy(name)
    elif isinstance(name, str):
        return Latest(name)
    elif hasattr(name, '__iter__'):
        return build_holder(name[0])


class CompoundedValueHolder(Accumulator):
    def __init__(self, left, right):
        self._returnSize = right.valueSize
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._window = self._left.window + self._right.window - 1
        self._containerSize = self._right._containerSize
        self._dependency = deepcopy(left.dependency)

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


class IIF(Accumulator):
    def __init__(self, cond, left, right):
        self._cond = build_holder(cond)
        self._returnSize = self._cond.valueSize
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._dependency = list(set(self._cond.dependency).union(set(self._cond.dependency).union(set(self._cond.dependency))))
        self._window = max(self._cond.window, self._left.window, self._right.window)
        self._containerSize = max(self._cond._containerSize, self._left._containerSize, self._right._containerSize)
        self._isFull = 0

    def push(self, data):
        self._cond.push(data)
        self._left.push(data)
        self._right.push(data)
        if self._isFull == 0 and self._cond.isFull and self._left.isFull and self._right.isFull:
            self._isFull = 1

    def result(self):
        return self._left.result() if self._cond.result() else self._right.result()


class BasicFunction(Accumulator):
    def __init__(self, dependency, func):
        super(BasicFunction, self).__init__(dependency)
        if self._isValueHolderContained:
            self._returnSize = self._dependency.valueSize
            self._window = self._dependency.window
            self._containerSize = self._dependency._containerSize
        else:
            self._returnSize = 1
            self._window = 1
            self._containerSize = 1
        self._func = func
        self._isFull = 0
        self._origValue = np.nan

    def push(self, data):
        value = super(BasicFunction, self).push(data)
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


class Exp(BasicFunction):
    def __init__(self, dependency):
        super(Exp, self).__init__(dependency, math.exp)


class Log(BasicFunction):
    def __init__(self, dependency):
        super(Log, self).__init__(dependency, math.log)


class Sqrt(BasicFunction):
    def __init__(self, dependency):
        super(Sqrt, self).__init__(dependency, math.sqrt)


# due to the fact that pow function is much slower than ** operator
class Pow(Accumulator):
    def __init__(self, dependency, n):
        super(Pow, self).__init__(dependency)
        if self._isValueHolderContained:
            self._returnSize = self._dependency.valueSize
            self._window = self._dependency.window
            self._containerSize = self._dependency._containerSize
        else:
            self._returnSize = 1
            self._window = 1
            self._containerSize = 1
        self._isFull = 0
        self._origValue = np.nan
        self.n = n

    def push(self, data):
        value = super(Pow, self).push(data)
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
            return self._origValue ** self.n
        except TypeError:
            return np.array(v ** self.n for v in self._origValue)


class Abs(BasicFunction):
    def __init__(self, dependency):
        super(Abs, self).__init__(dependency, abs)


class Sign(BasicFunction):
    def __init__(self, dependency):

        def sign(x):
            try:
                if x >= 0:
                    return 1
                else:
                    return -1
            except ValueError:
                raise TypeError

        super(Sign, self).__init__(dependency, sign)


class Acos(BasicFunction):
    def __init__(self, dependency):
        super(Acos, self).__init__(dependency, math.acos)


class Acosh(BasicFunction):
    def __init__(self, dependency):
        super(Acosh, self).__init__(dependency, math.acosh)


class Asin(BasicFunction):
    def __init__(self, dependency):
        super(Asin, self).__init__(dependency, math.asin)


class Asinh(BasicFunction):
    def __init__(self, dependency):
        super(Asinh, self).__init__(dependency, math.asinh)
