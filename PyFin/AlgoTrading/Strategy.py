# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod
import datetime as dt
from PyFin.AlgoTrading.Event import SignalEvent
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder


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
        self.count += 1
        for s in self._pNames[0]:
            securityValue = {}
            if self.count % 2:
                securityValue['PE'] = float(self.count)
            fields = self._pNames[0][s]
            try:
                value = self.bars.getLatestBarValue(s, fields)
                securityValue[fields] = value
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