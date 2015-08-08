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


class MovingAverageCrossStrategy(Strategy):

    def __init__(self,
                 bars,
                 events,
                 shortWindow=10,
                 longWindow=60):
        self.bars = bars
        self.symbolList = self.bars.symbolList
        self.events = events
        self.short_sma = MA(shortWindow, 'adj_close')#['AAPL']
        self.long_sma = MA(longWindow, 'adj_close')#['AAPL']
        self.bought = self._calculateInitialBought()

    def calculateSignals(self, event):
        for s in self.symbolList:
            short_sma = self.short_sma.value['AAPL']
            long_sma = self.long_sma.value['AAPL']
            symbol = s
            currDt = self.bars.getLatestBarDatetime(s)
            if short_sma > long_sma and self.bought[s] == 'OUT':
                print("{0}: BUY".format(currDt))
                sigDir = 'LONG'
                self.order(symbol, sigDir)
                self.bought[s] = 'LONG'
            if short_sma < long_sma and self.bought[s] == "LONG":
                print("{0}: SELL".format(currDt))
                sigDir = 'EXIT'
                self.order(symbol, sigDir)
                self.bought[s] = 'OUT'

    def _calculateInitialBought(self):
        self._subscribe()
        bought = {}
        for s in self.symbolList:
            bought[s] = 'OUT'
        return bought

if __name__ == "__main__":
    csvDir = "d:/"
    symbolList = ['AAPL']
    initialCapital = 100000.0
    heartbeat = 0.0
    startDate = dt.datetime(1990, 1, 1)

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
