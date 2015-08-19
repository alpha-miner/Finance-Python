# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

from enum import IntEnum
from enum import unique


@unique
class OptionType(IntEnum):
    Call = 1
    Put = -1
