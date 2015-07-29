# -*- coding: utf-8 -*-
u"""
Created on 2015-7-26

@author: cheng.li
"""

from abc import ABCMeta
from abc import abstractmethod
from copy import deepcopy


class Accumulator(object):

    __metaclass__ = ABCMeta

    def __init__(self, pNames):
        if hasattr(pNames, '__iter__') and len(pNames) >= 2:
            self._pNames = pNames
        elif hasattr(pNames, '__iter__') and len(pNames) == 1:
            self._pNames = pNames[0]
        elif hasattr(pNames, '__iter__'):
            raise RuntimeError("parameters' name list should not be empty")
        else:
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

    def __sub__(self, right):
        if isinstance(right, Accumulator):
            return MinusedValueHolder(self, right)
        return MinusedValueHolder(self, Identity(right))

    def __mul__(self, right):
        if isinstance(right, Accumulator):
            return MultipliedValueHolder(self, right)
        return MultipliedValueHolder(self, Identity(right))

    def __div__(self, right):
        if isinstance(right, Accumulator):
            return DividedValueHolder(self, right)
        return DividedValueHolder(self, Identity(right))

    def __truediv__(self, right):
        return self.__div__(right)

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

