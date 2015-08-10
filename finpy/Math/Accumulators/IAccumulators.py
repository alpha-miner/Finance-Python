# -*- coding: utf-8 -*-
u"""
Created on 2015-7-26

@author: cheng.li
"""

from abc import ABCMeta
from abc import abstractmethod
from copy import deepcopy
import math


class Accumulator(object):

    __metaclass__ = ABCMeta

    def __init__(self, pNames):
        if isinstance(pNames, Accumulator):
            self._isValueHolderContained = True
        else:
            self._isValueHolderContained = False
        if hasattr(pNames, '__iter__') and len(pNames) >= 2:
            for name in pNames:
                assert isinstance(name, str), '{0} in pNames should be a plain string. But it is {1}'.format(name, type(name))
            self._pNames = pNames
        elif hasattr(pNames, '__iter__') and len(pNames) == 1:
            for name in pNames:
                assert isinstance(name, str), '{0} in pNames should be a plain string. But it is {1}'.format(name, type(name))
            self._pNames = pNames[0]
        elif hasattr(pNames, '__iter__'):
            raise RuntimeError("parameters' name list should not be empty")
        else:
            assert isinstance(pNames, str) or isinstance(pNames, Accumulator), '{0} in pNames should be a plain string or an value holder. But it is {1}'.format(pNames, type(pNames))
            self._pNames = pNames

    def push(self, **kwargs):
        if not self._isValueHolderContained:
            if isinstance(self._pNames, str):
                if self._pNames in kwargs:
                    return kwargs[self._pNames]
                else:
                    return None
            elif hasattr(self._pNames, '__iter__'):
                try:
                    return tuple(kwargs[p] for p in self._pNames)
                except KeyError:
                    return None
        else:
            self._pNames.push(**kwargs)
            return self._pNames.result()

    @abstractmethod
    def result(self):
        raise NotImplementedError("result method is not implemented for Accumulator class")

    @property
    def value(self):
        return self.result()

    def __add__(self, right):
        if isinstance(right, Accumulator):
            if self._returnSize == right._returnSize:
                return AddedValueHolder(self, right)
            elif self._returnSize == 1:
                return AddedValueHolder(Identity(self, right._returnSize), right)
        return AddedValueHolder(self, Identity(right, self._returnSize))

    def __radd__(self, left):
        return AddedValueHolder(self, Identity(left, self._returnSize))

    def __sub__(self, right):
        if isinstance(right, Accumulator):
            if self._returnSize == right._returnSize:
                return MinusedValueHolder(self, right)
            elif self._returnSize == 1:
                return MinusedValueHolder(Identity(self, right._returnSize), right)
        return MinusedValueHolder(self, Identity(right, self._returnSize))

    def __rsub__(self, left):
        return MinusedValueHolder(Identity(left, self._returnSize), self)

    def __mul__(self, right):
        if isinstance(right, Accumulator):
            if self._returnSize == right._returnSize:
                return MultipliedValueHolder(self, right)
            elif self._returnSize == 1:
                return MultipliedValueHolder(Identity(self, right._returnSize), right)
        return MultipliedValueHolder(self, Identity(right, self._returnSize))

    def __rmul__(self, left):
        return MultipliedValueHolder(self, Identity(left, self._returnSize))

    def __div__(self, right):
        if isinstance(right, Accumulator):
            if self._returnSize == right._returnSize:
                return DividedValueHolder(self, right)
            elif self._returnSize == 1:
                return DividedValueHolder(Identity(self, right._returnSize), right)
        return DividedValueHolder(self, Identity(right, self._returnSize))

    def __rdiv__(self, left):
        return DividedValueHolder(Identity(left, self._returnSize), self)

    # only work for python 3
    def __truediv__(self, right):
        return self.__div__(right)

    # only work for python 3
    def __rtruediv__(self, left):
        return self.__rdiv__(left)

    def __le__(self, right):
        if isinstance(right, Accumulator):
            if self._returnSize == right._returnSize:
                return LeOperatorValueHolder(self, right)
            elif self._returnSize == 1:
                return LeOperatorValueHolder(Identity(self, right._returnSize), right)
        return LeOperatorValueHolder(self, Identity(right, self._returnSize))

    def __lt__(self, right):
        if isinstance(right, Accumulator):
            if self._returnSize == right._returnSize:
                return LtOperatorValueHolder(self, right)
            elif self._returnSize == 1:
                return LtOperatorValueHolder(Identity(self, right._returnSize), right)
        return LtOperatorValueHolder(self, Identity(right, self._returnSize))

    def __ge__(self, right):
        if isinstance(right, Accumulator):
            if self._returnSize == right._returnSize:
                return GeOperatorValueHolder(self, right)
            elif self._returnSize == 1:
                return GeOperatorValueHolder(Identity(self, right._returnSize), right)
        return GeOperatorValueHolder(self, Identity(right, self._returnSize))

    def __gt__(self, right):
        if isinstance(right, Accumulator):
            if self._returnSize == right._returnSize:
                return GtOperatorValueHolder(self, right)
            elif self._returnSize == 1:
                return GtOperatorValueHolder(Identity(self, right._returnSize), right)
        return GtOperatorValueHolder(self, Identity(right, self._returnSize))

    def __xor__(self, right):
        if isinstance(right, Accumulator):
            return ListedValueHolder(self, right)
        return ListedValueHolder(self, Identity(right, 1))

    def __rxor__(self, left):
        return ListedValueHolder(Identity(left, 1), self)

    def __rshift__(self, right):
        if isinstance(right, Accumulator):
            return CompoundedValueHolder(self, right)
        try:
            return CompoundedValueHolder(self, right())
        except:
            pass

        try:
            return right(self)
        except:
            raise RuntimeError('{0} is not recogonized as a valid operator'.format(right))

    def __neg__(self):
        return NegativeValueHolder(self)

    def __getitem__(self, item):
        return TruncatedValueHolder(self, item)


class NegativeValueHolder(Accumulator):

    def __init__(self, valueHolder):
        self._returnSize = valueHolder._returnSize
        self._valueHolder = deepcopy(valueHolder)
        self._dependency = valueHolder._dependency

    def push(self, **kwargs):
        self._valueHolder.push(**kwargs)

    def result(self):
        res = self._valueHolder.result()
        if self._returnSize > 1:
            return tuple(-r for r in res)
        else:
            return -res


class ListedValueHolder(Accumulator):
    def __init__(self, left, right):
        self._returnSize = left._returnSize + right._returnSize
        self._left = deepcopy(left)
        self._right = deepcopy(right)
        self._pNames = list(set(left._pNames).union(set(right._pNames)))
        self._dependency = max(self._left._dependency, self._right._dependency)

    def push(self, **kwargs):
        self._left.push(**kwargs)
        self._right.push(**kwargs)

    def result(self):
        resLeft = self._left.result()
        resRight = self._right.result()

        if not hasattr(resLeft, '__iter__'):
            resLeft = (resLeft,)
        if not hasattr(resRight, '__iter__'):
            resRight = (resRight,)
        return tuple(resLeft) + tuple(resRight)


class TruncatedValueHolder(Accumulator):
    def __init__(self, valueHolder, item):
        if valueHolder._returnSize == 1:
            raise RuntimeError("scalar valued holder ({0}) can't be sliced".format(valueHolder))
        if isinstance(item, slice):
            self._start = item.start
            self._stop = item.stop
            length = item.stop - item.start
            if length < 0:
                length += valueHolder._returnSize
            if length < 0:
                raise RuntimeError('start {0:d} and end {0:d} are not compatible'.format(self._start, self._stop))
            self._returnSize = length
        else:
            self._start = item
            self._stop = None
            self._returnSize = 1

        self._valueHolder = valueHolder
        self._dependency = self._valueHolder._dependency

    def push(self, **kwargs):
        self._valueHolder.push(**kwargs)

    def result(self):
        if self._stop is None:
            return self._valueHolder.result()[self._start]
        return self._valueHolder.result()[self._start:self._stop]


class CombinedValueHolder(Accumulator):

    def __init__(self, left, right):
        assert left._returnSize == right._returnSize
        self._returnSize = left._returnSize
        self._left = deepcopy(left)
        self._right = deepcopy(right)
        self._pNames = list(set(left._pNames).union(set(right._pNames)))
        self._dependency = max(self._left._dependency, self._right._dependency)
        self._window = self._dependency + 1

    def push(self, **kwargs):
        self._left.push(**kwargs)
        self._right.push(**kwargs)


class AddedValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(AddedValueHolder, self).__init__(left, right)

    def result(self):
        res1 = self._left.result()
        res2 = self._right.result()
        if self._returnSize > 1:
            return tuple(r1 + r2 for r1, r2 in zip(res1, res2))
        return res1 + res2


class MinusedValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(MinusedValueHolder, self).__init__(left, right)

    def result(self):
        res1 = self._left.result()
        res2 = self._right.result()
        if self._returnSize > 1:
            return tuple(r1 - r2 for r1, r2 in zip(res1, res2))
        return res1 - res2


class MultipliedValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(MultipliedValueHolder, self).__init__(left, right)

    def result(self):
        res1 = self._left.result()
        res2 = self._right.result()
        if self._returnSize > 1:
            return tuple(r1 * r2 for r1, r2 in zip(res1, res2))
        return res1 * res2


class DividedValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(DividedValueHolder, self).__init__(left, right)

    def result(self):
        res1 = self._left.result()
        res2 = self._right.result()
        if self._returnSize > 1:
            return tuple(r1 / r2 for r1, r2 in zip(res1, res2))
        return res1 / res2


class LtOperatorValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(LtOperatorValueHolder, self).__init__(left, right)

    def result(self):
        res1 = self._left.result()
        res2 = self._right.result()
        if self._returnSize > 1:
            return tuple(r1 < r2 for r1, r2 in zip(res1, res2))
        return res1 < res2


class LeOperatorValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(LeOperatorValueHolder, self).__init__(left, right)

    def result(self):
        res1 = self._left.result()
        res2 = self._right.result()
        if self._returnSize > 1:
            return tuple(r1 <= r2 for r1, r2 in zip(res1, res2))
        return res1 <= res2


class GtOperatorValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(GtOperatorValueHolder, self).__init__(left, right)

    def result(self):
        res1 = self._left.result()
        res2 = self._right.result()
        if self._returnSize > 1:
            return tuple(r1 > r2 for r1, r2 in zip(res1, res2))
        return res1 > res2


class GeOperatorValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(GeOperatorValueHolder, self).__init__(left, right)

    def result(self):
        res1 = self._left.result()
        res2 = self._right.result()
        if self._returnSize > 1:
            return tuple(r1 >= r2 for r1, r2 in zip(res1, res2))
        return res1 >= res2


class Identity(Accumulator):

    def __init__(self, value, n=1):
        if isinstance(value, Accumulator):
            assert value._returnSize == 1, "Identity can only be applied to single return value holder"
            self._dependency = value._dependency
            self._isValueHolder = True
            self._window = self._dependency + 1
            self._pNames = value._pNames
        else:
            self._dependency = 0
            self._isValueHolder = False
            self._window = 1
            self._pNames = []
        self._value = value
        self._returnSize = n

    def push(self, **kwargs):
        if self._isValueHolder:
            self._value.push(**kwargs)

    def result(self):
        if self._isValueHolder:
            value = self._value.result()
        else:
            value = self._value
        if self._returnSize == 1:
            return value
        else:
            return (value,) * self._returnSize


class CompoundedValueHolder(Accumulator):

    def __init__(self, left, right):
        self._returnSize = right._returnSize
        self._left = deepcopy(left)
        self._right = deepcopy(right)
        self._dependency = self._left._dependency + self._right._dependency
        self._pNames = deepcopy(left._pNames)

        if hasattr(self._right._pNames, '__iter__'):
            assert left._returnSize == len(self._right._pNames)
        else:
            assert left._returnSize == 1

    def push(self, **kwargs):
        self._left.push(**kwargs)
        values = self._left.result()
        if hasattr(values, '__iter__'):
            parameters = dict((name, value) for name, value in zip(self._right._pNames, values))
        else:
            parameters = {self._right._pNames:values}
        self._right.push(**parameters)

    def result(self):
        return self._right.result()


class BasicFunction(Accumulator):

    def __init__(self, valueHolder, func, *args, **kwargs):
        self._returnSize = valueHolder._returnSize
        self._valueHolder = deepcopy(valueHolder)
        self._dependency = valueHolder._dependency
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._window = self._dependency + 1
        self._pNames = deepcopy(valueHolder._pNames)

    def push(self, **kwargs):
        self._valueHolder.push(**kwargs)

    def result(self):
        origValue = self._valueHolder.result()

        if hasattr(origValue, '__iter__'):
            return tuple(self._func(v, *self._args, **self._kwargs) for v in origValue)
        else:
            return self._func(origValue, *self._args, **self._kwargs)


def Exp(valueHolder):
    return BasicFunction(valueHolder, math.exp)


def Log(valueHolder):
    return BasicFunction(valueHolder, math.log)


def Sqrt(valueHolder):
    return BasicFunction(valueHolder, math.sqrt)


# due to the fact that pow function is much slower than ** operator
class Pow(Accumulator):
    def __init__(self, valueHolder, n):
        self._returnSize = valueHolder._returnSize
        self._valueHolder = deepcopy(valueHolder)
        self._dependency = valueHolder._dependency
        self._n = n
        self._window = self._dependency + 1
        self._pNames = deepcopy(valueHolder._pNames)

    def push(self, **kwargs):
        self._valueHolder.push(**kwargs)

    def result(self):
        origValue = self._valueHolder.result()
        if hasattr(origValue, '__iter__'):
            return tuple(v ** self._n for v in origValue)
        else:
            return origValue ** self._n


def Abs(valueHolder):
    return BasicFunction(valueHolder, abs)


def Acos(valueHolder):
    return BasicFunction(valueHolder, math.acos)


def Acosh(valueHolder):
    return BasicFunction(valueHolder, math.acosh)


def Asin(valueHolder):
    return BasicFunction(valueHolder, math.asin)


def Asinh(valueHolder):
    return BasicFunction(valueHolder, math.asinh)