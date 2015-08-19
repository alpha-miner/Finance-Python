# -*- coding: utf-8 -*-
u"""
Created on 2015-7-15

@author: cheng.li
"""

from enum import IntEnum
from enum import unique


@unique
class DateGeneration(IntEnum):
    Zero = 0
    Backward = 1
    Forward = 2
