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
            assert isinstance(pNames, str), '{0} in pNames should be a plain string. But it is {1}'.format(pNames, type(pNames))
            self._pNames = pNames

    @abstractmethod
    def push(self, **kwargs):
        raise NotImplementedError("push method is not implemented for Accumulator class")

    @abstractmethod
    def result(self):
        raise NotImplementedError("result method is not implemented for Accumulator class")

    def __add__(self, right):
        if isinstance(right, Accumulator):
            return AddedValueHolder(self, right)
        return AddedValueHolder(self, Identity(right))

    def __radd__(self, left):
        if isinstance(left, Accumulator):
            return AddedValueHolder(self, left)
        return AddedValueHolder(self, Identity(left))

    def __sub__(self, right):
        if isinstance(right, Accumulator):
            return MinusedValueHolder(self, right)
        return MinusedValueHolder(self, Identity(right))

    def __rsub__(self, left):
        if isinstance(left, Accumulator):
            return MinusedValueHolder(left, self)
        return MinusedValueHolder(Identity(left), self)

    def __mul__(self, right):
        if isinstance(right, Accumulator):
            return MultipliedValueHolder(self, right)
        return MultipliedValueHolder(self, Identity(right))

    def __rmul__(self, left):
        if isinstance(left, Accumulator):
            return MultipliedValueHolder(self, left)
        return MultipliedValueHolder(self, Identity(left))

    def __div__(self, right):
        if isinstance(right, Accumulator):
            return DividedValueHolder(self, right)
        return DividedValueHolder(self, Identity(right))

    def __rdiv__(self, left):
        if isinstance(left, Accumulator):
            return DividedValueHolder(left, self)
        return DividedValueHolder(Identity(left), self)

    def __truediv__(self, right):
        return self.__div__(right)

    def __rtruediv__(self, left):
        return self.__rdiv__(left)

    def __rshift__(self, right):
        return CompoundedValueHolder(self, right)


class CombinedValueHolder(Accumulator):

    def __init__(self, left, right):
        assert left._returnSize == right._returnSize
        self._returnSize = left._returnSize
        self._left = deepcopy(left)
        self._right = deepcopy(right)
        self._dependency = max(self._left._dependency, self._right._dependency)

    def push(self, **kwargs):
        self._left.push(**kwargs)
        self._right.push(**kwargs)


class AddedValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(AddedValueHolder, self).__init__(left, right)

    def result(self):
        return self._left.result() + self._right.result()


class MinusedValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(MinusedValueHolder, self).__init__(left, right)

    def result(self):
        return self._left.result() - self._right.result()


class MultipliedValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(MultipliedValueHolder, self).__init__(left, right)

    def result(self):
        return self._left.result() * self._right.result()


class DividedValueHolder(CombinedValueHolder):

    def __init__(self, left, right):
        super(DividedValueHolder, self).__init__(left, right)

    def result(self):
        return self._left.result() / self._right.result()


class Identity(Accumulator):
    def __init__(self, value):
        self._value = value

    def push(self, **kwargs):
        pass

    def result(self):
        return self._value


class CompoundedValueHolder(Accumulator):

    def __init__(self, left, right):
        self._returnSize = right._returnSize
        self._left = deepcopy(left)
        self._right = deepcopy(right)
        self._dependency = self._left._dependency + self._right._dependency

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

    def __init__(self, valueHolder, func):
        self._returnSize = valueHolder._returnSize
        self._valueHolder = deepcopy(valueHolder)
        self._dependency = valueHolder._dependency
        self._func = func

    def push(self, **kwargs):
        self._valueHolder.push(**kwargs)

    def result(self):
        origValue = self._valueHolder.result()

        if hasattr(origValue, '__iter__'):
            return tuple(self._func(v) for v in origValue)
        else:
            return self._func(origValue)


def Exp(valueHolder):
    return BasicFunction(valueHolder, math.exp)


def Log(valueHolder):
    return BasicFunction(valueHolder, math.log)


def Sqrt(valueHolder):
    return BasicFunction(valueHolder, math.sqrt)


def Abs(valueHolder):
    return BasicFunction(valueHolder, abs)
