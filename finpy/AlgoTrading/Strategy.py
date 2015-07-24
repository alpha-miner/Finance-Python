# -*- coding: utf-8 -*-
u"""
Created on 2015-7-24

@author: cheng.li
"""


from abc import ABCMeta
from abc import abstractmethod


class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def calculateSignals(self):
        raise NotImplementedError()
