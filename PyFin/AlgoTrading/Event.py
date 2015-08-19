# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


class Event(object):
    pass


class MarketEvent(Event):

    def __init__(self):
        self.type = 'MARKET'


class SignalEvent(Event):

    def __init__(self, strategyId, symbol, datetime, signalType, strength):
        self.type = 'SIGNAL'
        self.strategyId = strategyId
        self.symbol = symbol
        self.datetime = datetime
        self.signalType = signalType
        self.strength = strength


class OrderEvent(Event):

    def __init__(self, symbol, orderType, quantity, direction):
        self.type = 'ORDER'
        self.symbol = symbol
        self.orderType = orderType
        self.quantity = quantity
        self.direction = direction

    def __str__(self):
        return "Order: Symbol = {0:s}, " \
               "Type = {1:s}, " \
               "Quantity = {2:s}, " \
               "Direction = {3:s}".format(self.symbol, self.orderType, self.quantity, self.direction)


class FillEvent(Event):

    def __init__(self, timeindex, symbol, exchange, quantity, direction, fillCost, commission=None):
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fillCost = fillCost

        # calculate commission
        if commission is None:
            self.commission = self._calculateIbCommission()
        else:
            self.commission = commission

    def _calculateIbCommission(self):
        if self.quantity <= 500:
            fullCost = max(1.3, 0.013 * self.quantity)
        else:
            fullCost = max(1.3, 0.008 * self.quantity)
        return fullCost

