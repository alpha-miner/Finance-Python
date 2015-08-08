# -*- coding: utf-8 -*-
u"""
Created on 2015-8-8

@author: cheng.li
"""

from finpy.Analysis.SecurityValueHolders import SecurityValueHolder
from finpy.Math.Accumulators.StatefulAccumulators import MovingAverage


class SecurityMovingAverage(SecurityValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingAverage, self).__init__(pNames, symbolList)
        self._window = window
        self._innerHolders = \
            {
                name: MovingAverage(self._window, self._pNames) for name in self._symbolList
            }

if __name__ == "__main__":
    # inializing the value holde
    symbolList = ['600000.XSHG', 'AAPL', 'GOOG', "Lenovo"]
    ma = SecurityMovingAverage(20, 'close')
    ma2 = SecurityMovingAverage(10, 'open')
    ma3 = ma['AAPL'] / ma - 3.0

    # prepare the data
    data = {'600000.XSHG': {'close': 6.0, 'open': 15.0},
            'AAPL': {'close': 12.0, 'open': 10.0},
            'GOOG': {'close': 24.0, 'open': 17.0}}

    data2 = {str(i): {'close': 3.0} for i in range(30)}
    data.update(data2)

    # push and pop
    for i in range(100):
        ma3.push(data)
        print(ma3.value)