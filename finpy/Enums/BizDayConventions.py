# -*- coding: utf-8 -*-
u"""
Created on 2015-7-9

@author: cheng.li
"""

from enum import IntEnum
from enum import unique


@unique
class BizDayConventions(IntEnum):
    Following = 0
    ModifiedFollowing = 1
    Preceding = 2
    ModifiedPreceding = 3
    Unadjusted = 4
    HalfMonthModifiedFollowing = 5
    Nearest = 6
