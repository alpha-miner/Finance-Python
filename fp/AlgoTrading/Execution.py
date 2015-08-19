# -*- coding: utf-8 -*-
u"""
Created on 2015-7-31

@author: cheng.li
"""

from abc import ABCMeta, abstractmethod
import datetime as dt

from fp.AlgoTrading.Event import FillEvent


class ExecutionHanlder(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def executeOrder(self, event):
        raise NotImplementedError()


class SimulatedExecutionHandler(ExecutionHanlder):

    def __init__(self, events):
        self.events = events

    def executeOrder(self, event):
        if event.type == 'ORDER':
            fill_event = FillEvent(dt.datetime.utcnow(),
                                   event.symbol,
                                   'ARCA',
                                   event.quantity,
                                   event.direction,
                                   None)
            self.events.put(fill_event)


