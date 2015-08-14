# -*- coding: utf-8 -*-
u"""
Created on 2015-7-21

@author: cheng.li
"""

from enum import IntEnum
from enum import unique


@unique
class NormalizingType(IntEnum):
    Null = 0
    BizDay = 1
    CalendarDay = 2
