# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import math
import numpy as np
from abc import ABCMeta
from abc import abstractmethod


class Accumulator(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def push(self, **kwargs):
        raise NotImplementedError("push method is not implemented for Accumulator class")

    @abstractmethod
    def result(self):
        raise NotImplementedError("result method is not implemented for Accumulator class")

    def __add__(self, right):
        return AddedValueHolder(self, right)

    def __sub__(self, right):
        return MinusedValueHolder(self, right)

    def __mul__(self, right):
        return MultipliedValueHolder(self, right)

    def __div__(self, right):
        return DividedValueHolder(self, right)

    def __truediv__(self, right):
        return self.__div__(right)

    def __rshift__(self, right):
        return CompoundedValueHolder(self, right)


class CombinedValueHolder(Accumulator):

    def __init__(self, left, right):
        assert left._returnSize == right._returnSize
        self._returnSize = left._returnSize
        self._left = left
        self._right = right

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


class CompoundedValueHolder(Accumulator):

    def __init__(self, left, right):
        self._returnSize = right._returnSize
        self._left = left
        self._right = right

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

class StatelessValueHolder(Accumulator):
    pass


class StatefulValueHolder(Accumulator):

    def __init__(self, window, pNames):
        assert window > 0, "window length should be greater than 0"
        self._returnSize = 1
        self._window = window
        self._con = []
        self._isFull = 0
        self._start = 0
        if hasattr(pNames, '__iter__') and len(pNames) >= 2:
            self._pNames = pNames
        elif hasattr(pNames, '__iter__') and len(pNames) == 1:
            self._pNames = pNames[0]
        elif hasattr(pNames, '__iter__'):
            raise RuntimeError("parameters' name list should not be empty")
        else:
            self._pNames = pNames

    @property
    def isFull(self):
        return self._isFull == 1

    @property
    def size(self):
        return len(self._con)

    def _dumpOneValue(self, value):
        if not hasattr(value, '__iter__'):
            popout = 0.0
        else:
            popout = [0.0] * len(value)

        if self._isFull == 1:
            # use list as circular queue
            popout = self._con[self._start]
            self._con[self._start] = value
            self._start = (self._start + 1) % self._window
        elif len(self._con) + 1 == self._window:
            self._con.append(value)
            self._isFull = 1
        else:
            self._con.append(value)
        return popout


class MovingMaxer(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingMaxer, self).__init__(window, pNames)

    def push(self, **kwargs):
        _ = self._dumpOneValue(kwargs[self._pNames])

    def result(self):
        return max(self._con)


class MovingMinumer(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingMinumer, self).__init__(window, pNames)

    def push(self, **kwargs):
        _ = self._dumpOneValue(kwargs[self._pNames])

    def result(self):
        return min(self._con)


class MovingSum(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingSum, self).__init__(window, pNames)
        self._runningSum = 0.0

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        popout = self._dumpOneValue(value)
        self._runningSum = self._runningSum - popout + value

    def result(self):
        return self._runningSum


class MovingAverager(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingAverager, self).__init__(window, pNames)
        self._runningSum = 0.0

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        popout = self._dumpOneValue(value)
        self._runningSum = self._runningSum - popout + value

    def result(self):
        if self._isFull:
            return self._runningSum / self._window
        else:
            return self._runningSum / self.size


class MovingPositiveAverager(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingPositiveAverager, self).__init__(window, pNames)
        self._runningPositiveSum = 0.0
        self._runningPositiveCount = 0

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        popout = self._dumpOneValue(value)
        if value > 0.0:
            self._runningPositiveCount += 1
            self._runningPositiveSum += value

        if popout > 0.0:
            self._runningPositiveCount -= 1
            self._runningPositiveSum -= popout

    def result(self):
        if self._runningPositiveCount == 0:
            return 0.0
        else:
            return self._runningPositiveSum / self._runningPositiveCount


class MovingNegativeAverager(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingNegativeAverager, self).__init__(window, pNames)
        self._runningNegativeSum = 0.0
        self._runningNegativeCount = 0

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        popout = self._dumpOneValue(value)
        if value < 0.0:
            self._runningNegativeCount += 1
            self._runningNegativeSum += value

        if popout < 0.0:
            self._runningNegativeCount -= 1
            self._runningNegativeSum -= popout

    def result(self):
        if self._runningNegativeCount == 0:
            return 0.0
        else:
            return self._runningNegativeSum / self._runningNegativeCount


class MovingVariancer(StatefulValueHolder):

    def __init__(self, window, pNames='x', isPopulation=False):
        super(MovingVariancer, self).__init__(window, pNames)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        popout = self._dumpOneValue(value)
        self._runningSum = self._runningSum - popout + value
        self._runningSumSquare = self._runningSumSquare - popout * popout + value * value

    def result(self):
        if self._isFull:
            tmp = self._runningSumSquare - self._runningSum * self._runningSum / self._window
            if self._isPop:
                return tmp / self._window
            else:
                return tmp / (self._window - 1)
        elif self.size >= 2:
            tmp = self._runningSumSquare - self._runningSum * self._runningSum / self.size
            if self._isPop:
                return tmp / self.size
            else:
                return tmp / (self.size - 1)
        else:
            raise RuntimeError("Container has less than 2 samples")


class MovingNegativeVariancer(StatefulValueHolder):

    def __init__(self, window, pNames='x', isPopulation=False):
        super(MovingNegativeVariancer, self).__init__(window, pNames)
        self._runningNegativeSum = 0.0
        self._runningNegativeSumSquare = 0.0
        self._runningNegativeCount = 0
        self._isPop = isPopulation

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        popout = self._dumpOneValue(value)
        if value < 0:
            self._runningNegativeSum += value
            self._runningNegativeSumSquare += value * value
            self._runningNegativeCount += 1
        if popout < 0:
            self._runningNegativeSum -= popout
            self._runningNegativeSumSquare -= popout * popout
            self._runningNegativeCount -= 1

    def result(self):
        if self._isPop:
            if self._runningNegativeCount >= 1:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / length
            else:
                raise RuntimeError("Negative population variance container has less than 1 samples")
        else:
            if self._runningNegativeCount >= 2:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / (length - 1)
            else:
                raise RuntimeError("Negative sample variance container has less than 2 samples")


class MovingCountedPositive(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingCountedPositive, self).__init__(window, pNames)
        self._counts = 0

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        popout = self._dumpOneValue(value)

        if value > 0:
            self._counts += 1
        if popout > 0:
            self._counts -= 1

    def result(self):
        return self._counts


class MovingCountedNegative(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingCountedNegative, self).__init__(window, pNames)
        self._counts = 0

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        popout = self._dumpOneValue(value)

        if value < 0:
            self._counts += 1
        if popout < 0:
            self._counts -= 1

    def result(self):
        return self._counts


# Calculator for one pair of series
class MovingCorrelation(StatefulValueHolder):

    def __init__(self, window, pNames=('x', 'y')):
        super(MovingCorrelation, self).__init__(window, pNames)
        self._runningSumLeft = 0.0
        self._runningSumRight = 0.0
        self._runningSumSquareLeft = 0.0
        self._runningSumSquareRight = 0.0
        self._runningSumCrossSquare = 0.0

    def push(self, **kwargs):
        value = [kwargs[self._pNames[0]], kwargs[self._pNames[1]]]
        popout = self._dumpOneValue(value)
        headLeft = popout[0]
        headRight = popout[1]

        # updating cached values
        self._runningSumLeft = self._runningSumLeft - headLeft + value[0]
        self._runningSumRight = self._runningSumRight - headRight + value[1]
        self._runningSumSquareLeft = self._runningSumSquareLeft - headLeft * headLeft + value[0] * value[0]
        self._runningSumSquareRight = self._runningSumSquareRight - headRight * headRight + value[1] * value[1]
        self._runningSumCrossSquare = self._runningSumCrossSquare - headLeft * headRight + value[0] * value[1]

    def result(self):

        if self._isFull:
            n = self._window
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          *(n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            denominator = math.sqrt(denominator)
            return nominator / denominator
        elif self.size >= 2:
            n = self.size
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          *(n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            denominator = math.sqrt(denominator)
            return nominator / denominator
        else:
            raise RuntimeError("Container has less than 2 samples")


class MovingCorrelationMatrix(StatefulValueHolder):

    def __init__(self, window, pNames='values'):
        super(MovingCorrelationMatrix, self).__init__(window, pNames)

    def push(self, **kwargs):
        values = kwargs[self._pNames]
        _ = self._dumpOneValue(values)

    def result(self):
        if len(self._con) >= 2:
            return np.corrcoef(np.matrix(self._con).T)
        else:
            raise RuntimeError("Container has less than 2 samples")


if __name__ == '__main__':

    addedHolder = MovingAverager(20, 'x') >> MovingAverager(20) >> MovingMinumer(20)

    for i in range(100):
        addedHolder.push(x=float(i))
        print(addedHolder.result())




