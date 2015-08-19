# -*- coding: utf-8 -*-
u"""
Created on 2015-7-9

@author: cheng.li
"""

from enum import IntEnum
from enum import unique


@unique
class Weekdays(IntEnum):
    Sunday = 1
    Monday = 2
    Tuesday = 3
    Wednesday = 4
    Thursday = 5
    Friday = 6
    Saturday = 7
