# -*- coding: utf-8 -*-
u"""
Created on 2015-8-13

@author: cheng.li
"""

from enum import Enum
from enum import unique


class StrEnum(str, Enum):
    pass


@unique
class Factors(StrEnum):
    CLOSE = 'close'
    PE = 'pe'
    OPEN = 'open'
    VOLUME = 'volume'
    HIGH = 'high'
    LOW = 'low'
