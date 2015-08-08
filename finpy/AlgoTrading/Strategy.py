# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
import datetime as dt
from finpy.AlgoTrading.Event import SignalEvent
from finpy.Analysis.SecurityValueHolders import SecurityValueHolder
from finpy.Analysis.SecurityValueHolders import NamedValueHolder

class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def calculateSignals(self, event):
        raise NotImplementedError()

    def _subscribe(self):
        self._subscribed = []
        self._pNames = tuple()
        for k, v in self.__dict__.items():
            if isinstance(v, SecurityValueHolder):
                self._subscribed.append(v)
                self._pNames = self._pNames + (v.dependency,)

    def _updateSubscribing(self):

        values = dict()
        for s in self.symbolList:
            securityValue = {}
            for name in self._pNames:
                try:
                    value = self.bars.getLatestBarValue(s, name)
                    securityValue[name] = value
                except:
                    pass
            values[s] = securityValue

        for subscriber in self._subscribed:
            subscriber.push(values)

    def monitoring(self):
        pass

    def order(self, symbol, signalDirection):
        currentDT = dt.datetime.utcnow()
        signal = SignalEvent(1, symbol, currentDT, signalDirection, 1.0)
        self.events.put(signal)