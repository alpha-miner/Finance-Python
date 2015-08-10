# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

import datetime as dt

from finpy.AlgoTrading.Strategy import Strategy
from finpy.AlgoTrading.Backtest import Backtest
from finpy.AlgoTrading.Data import HistoricalCSVDataHandler
from finpy.AlgoTrading.Execution import SimulatedExecutionHandler
from finpy.AlgoTrading.Portfolio import Portfolio
from finpy.Analysis.TechnicalAnalysis import SecurityMovingAverage as MA
from finpy.Analysis.TechnicalAnalysis import SecurityMovingMax as MAX
from finpy.Analysis.TechnicalAnalysis import SecurityMovingMinimum as MIN
from finpy.Analysis import SecurityShiftedValueHolder as Shift
from finpy.Analysis import SecurityCompoundedValueHolder as Compounded


class MovingAverageCrossStrategy(Strategy):

    def __init__(self,
                 bars,
                 events,
                 shortWindow=10):
        self.bars = bars
        self.symbolList = self.bars.symbolList
        self.events = events
        self.short_sma = MA(shortWindow, 'adj_close', symbolList)
        self.sample = MA(2, self.short_sma)
        self.shifted = Shift(MA(shortWindow, 'adj_close', symbolList), 1)
        self.ret = self.short_sma / self.shifted - 1.0
        self.compounded = Compounded(self.short_sma, MAX(3))
        self.compounded2 = Compounded(self.compounded, MIN(3))
        self.bought = self._calculateInitialBought()
        self.count = 0

    def calculateSignals(self, event):
        #print("{0} vs {1} vs {2} vs {3}".format(self.short_sma.value,
        #                                        self.compounded.value,
        #                                        self.compounded2.value,
        #                                        self.ret.value))
        print("{0}".format(self.sample.value))
        # for s in self.symbolList:
        #     symbol = s
        #     currDt = self.bars.getLatestBarDatetime(s)
        #     if short_sma[s] > long_sma[s] and self.bought[s] == 'OUT':
        #         #print("{0}: BUY {1}".format(currDt, s))
        #         sigDir = 'LONG'
        #         self.order(symbol, sigDir)
        #         self.bought[s] = 'LONG'
        #     if short_sma[s] < long_sma[s] and self.bought[s] == "LONG":
        #         #print("{0}: SELL {1}".format(currDt, s))
        #         sigDir = 'EXIT'
        #         self.order(symbol, sigDir)
        #         self.bought[s] = 'OUT'

    def _calculateInitialBought(self):
        self._subscribe()
        bought = {}
        for s in self.symbolList:
            bought[s] = 'OUT'
        return bought

if __name__ == "__main__":
    csvDir = "d:/"
    symbolList = ['AAPL', 'MSFT', 'IBM']
    initialCapital = 100000.0
    heartbeat = 0.0
    startDate = dt.datetime(2014, 1, 1)

    backtest = Backtest(csvDir,
                        symbolList,
                        initialCapital,
                        heartbeat,
                        startDate,
                        HistoricalCSVDataHandler,
                        SimulatedExecutionHandler,
                        Portfolio,
                        MovingAverageCrossStrategy)

    backtest.simulateTrading()
