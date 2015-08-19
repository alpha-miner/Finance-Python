# -*- coding: utf-8 -*-
u"""
Created on 2015-7-9

@author: cheng.li
"""

from enum import IntEnum
from enum import unique


@unique
class TimeUnits(IntEnum):
    BDays = 0
    Days = 1
    Weeks = 2
    Months = 3
    Years = 4
