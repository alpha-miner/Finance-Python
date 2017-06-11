# -*- coding: utf-8 -*-
u"""
Created on 2017-6-11

@author: cheng.li
"""

from enum import IntEnum


class Compounding(IntEnum):

    Simple = 0
    Compounded = 1
    Continuous = 2
    SimpleThenCompounded = 3
    CompoundedThenSimple = 4
