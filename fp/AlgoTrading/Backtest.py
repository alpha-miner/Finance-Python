# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

try:
    import Queue as queue
except ImportError:
    import queue
import time


class Backtest(object):

    def __init__(self,
                 csv_dir,
                 symbol_list,
                 initial_capital,
                 heartbeat,
                 start_date,
                 data_handler,
                 execution_handler,
                 portfolio,
                 strategy):
        self.csvDir = csv_dir
        self.symbolList = symbol_list
        self.initialCapital = initial_capital
        self.heartbeat = heartbeat
        self.startDate = start_date
        self.dataHandlerCls = data_handler
        self.executionHanlderCls = execution_handler
        self.portfolioCls = portfolio
        self.strategyCls = strategy

        self.events = queue.Queue()

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self._generateTradingInstance()

    def _generateTradingInstance(self):
        self.dataHandler = self.dataHandlerCls(self.events, self.csvDir, self.symbolList)
        self.strategy = self.strategyCls(self.dataHandler, self.events)
        self.portfolio = self.portfolioCls(self.dataHandler,
                                           self.events,
                                           self.startDate,
                                           self.initialCapital)
        self.executionHanlder = self.executionHanlderCls(self.events)

    def _runBacktest(self):

        i = 0
        while True:
            i += 1
            if self.dataHandler.continueBacktest == True:
                self.dataHandler.updateBars()
            else:
                break

            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                if event is not None:
                    if event.type == 'MARKET':
                        self.strategy._updateSubscribing()
                        self.strategy.calculateSignals(event)
                        self.portfolio.updateTimeindex()
                    elif event.type == 'SIGNAL':
                        self.signals += 1
                        self.portfolio.updateSignal(event)
                    elif event.type == 'ORDER':
                        self.orders += 1
                        self.executionHanlder.executeOrder(event)
                    elif event.type == 'FILL':
                        self.fills += 1
                        self.portfolio.updateFill(event)

            time.sleep(self.heartbeat)

    def _outputPerformance(self):
        self.portfolio.createEquityCurveDataframe()
        print(self.portfolio.equityCurve.tail(50))

        print("Signals: {0:d}".format(self.signals))
        print("Orders : {0:d}".format(self.orders))
        print("Fills  : {0:d}".format(self.fills))

    def simulateTrading(self):
        self._runBacktest()
        #self._outputPerformance()

