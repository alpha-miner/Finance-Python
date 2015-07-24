# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""

from finpy.AlgoTrading.Event import OrderEvent


class Portfolio(object):

    def __init__(self, bars, events, startDate, initialCapital=100000.0):
        self.bars = bars
        self.events = events
        self.symbolList = self.bars.symbolList
        self.startDate = startDate
        self.initialCapital = initialCapital

        self.allPositions = self.constructAllPositions()
        self.currentPosition = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])

        self.allHoldings = self.costructAllHoldings()
        self.currentHoldings = self.constructCurrentHoldings()

    def constructAllPositions(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])
        d['datetime'] = self.startDate
        return [d]

    def constructAllHoldings(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])
        d['datetime'] = self.startDate
        d['cash'] = self.initialCapital
        d['commission'] = 0.0
        d['total'] = self.initialCapital
        return [d]

    def constructCurrentHoldings(self):
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])
        d['datetime'] = self.startDate
        d['cash'] = self.initialCapital
        d['commission'] = 0.0
        d['total'] = self.initialCapital
        return d

    def updateTimeindex(self, event):
        latestDatetime = self.bars.getLatestBarDatetime(self.symbolList[0])
        dp = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])
        dp['date'] = latestDatetime

        for s in self.symbolList:
            dp[s] = self.currentPosition[s]

        self.allPositions.append(dp)

        dh = dict((k, v) for k, v in [(s, 0) for s in self.symbolList])
        dh['datetime'] = latestDatetime
        dh['cash'] = self.currentHoldings['cash']
        dh['commission'] = self.currentHoldings['commission']
        dh['total'] = self.currentHoldings['cash']

        for s in self.symbolList:
            marketValue = self.currentPosition[s] * self.bars.getLatestBarValue(s, 'adj_close')
            dh[s] = marketValue
            dh['total'] += marketValue

        self.allHoldings.append(dh)

    def updatePositionFromFill(self, fill):
        fillDir = 0
        if fill.direction == 'BUY':
            fillDir = 1
        if fill.direction == 'SELL':
            fillDir = -1

        self.currentPosition[fill.symbol] += fillDir * fill.quantity

    def updateHoldingsFromFill(self, fill):
        fillDir = 0
        if fill.direction == 'BUY':
            fillDir = 1
        if fill.direction == 'SELL':
            fillDir = -1

        fillCost = self.bars.getLatestBarValue(fill.symbol, 'adj_close')
        cost = fillDir * fillCost * fill.quantity
        self.currentHoldings[fill.symbol] += cost
        self.currentHoldings['commission'] += fill.commission
        self.currentHoldings['cash'] -= (cost + fill.commission)
        self.currentHoldings['total'] -= (cost + fill.commission)

    def updateFill(self, event):
        if event.type == 'FILL':
            self.updatePositionFromFill(event)
            self.updateHoldingsFromFill(event)

    def generateNaiveOrder(self, signal):
        order = None

        symbol = signal.symbol
        direction = signal.signalType

        mktQuantity = 100
        curQuantity = self.currentPosition[symbol]
        orderType = 'MKT'

        if direction == 'LONG' and curQuantity == 0:
            order = OrderEvent(symbol, orderType, mktQuantity, 'BUY')
        if direction == 'SHORT' and curQuantity == 0:
            order = OrderEvent(symbol, orderType, mktQuantity, 'SELL')

        if direction == 'EXIT' and curQuantity > 0:
            order = OrderEvent(symbol, orderType, abs(curQuantity), 'SELL')
        if direction == 'EXIT' and curQuantity < 0:
            order = OrderEvent(symbol, orderType, abs(curQuantity), 'BUY')

        return order

    def updateSignal(self, event):
        if event.type == 'SIGNAL':
            orderEvent = self.generateNaiveOrder(event)
            self.events.put(orderEvent)

