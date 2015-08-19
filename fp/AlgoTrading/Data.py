# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
import os

import pandas.io as io
import numpy as np

from fp.AlgoTrading.Event import MarketEvent


class DataHandler(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def getLatestBar(self, symbol):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBars(self, symbol, N=1):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBarDatetime(self, symbol):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBarValue(self, symbol, valType):
        raise NotImplementedError()

    @abstractmethod
    def getLatestBarsValues(self, symbol, valType, N=1):
        raise NotImplementedError()

    @abstractmethod
    def updateBars(self):
        raise NotImplementedError()


class HistoricalCSVDataHandler(DataHandler):

    def __init__(self, events, csvDir, symbolList):
        self.events = events
        self.csvDir = csvDir
        self.symbolList = symbolList
        self.symbolData = {}
        self.latestSymbolData = {}
        self.continueBacktest = True

        self._openConvertCSVFiles()

    def getLatestBar(self, symbol):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return barsList[-1]

    def getLatestBars(self, symbol, N=1):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return barsList[-N:]

    def getLatestBarDatetime(self, symbol):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return barsList[-1][0]

    def getLatestBarValue(self, symbol, valType):
        try:
            barsList = self.latestSymbolData[symbol]
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return getattr(barsList[-1][1], valType)

    def getLatestBarsValues(self, symbol, valType, N=1):
        try:
            barsList = self.getLatestBars(symbol, N)
        except KeyError:
            raise RuntimeError("the symbol {0:s} is not available in the historical data set".format(symbol))
        else:
            return np.array([getattr(b[1], valType) for b in barsList])

    def updateBars(self):
        for s in self.symbolList:
            try:
                bar = next(self._getNewBar(s))
            except StopIteration:
                self.continueBacktest = False
            else:
                if bar is not None:
                    self.latestSymbolData[s].append(bar)
        self.events.put(MarketEvent())

    def _getNewBar(self, symbol):
        for b in self.symbolData[symbol]:
            yield b

    def _openConvertCSVFiles(self):
        combIndex = None
        for s in self.symbolList:
            filePath = os.path.join(self.csvDir, "{0:s}.csv".format(s))
            self.symbolData[s] = io.parsers.read_csv(filePath,
                                                     header=0,
                                                     index_col=0,
                                                     parse_dates=True,
                                                     names=['datetime', 'open', 'high', 'low', 'close', 'volume', 'adj_close']).sort()

            if combIndex is None:
                combIndex = self.symbolData[s].index
            else:
                combIndex.union(self.symbolData[s].index)

            self.latestSymbolData[s] = []

        for s in self.symbolList:
            self.symbolData[s] = self.symbolData[s].reindex(index=combIndex, method='pad').iterrows()

