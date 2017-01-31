# -*- coding: utf-8 -*-
u"""
Created on 2017-1-30

@author: cheng.li
"""

cdef public enum BizDayConventions:
    Following = 0
    ModifiedFollowing = 1
    Preceding = 2
    ModifiedPreceding = 3
    Unadjusted = 4
    HalfMonthModifiedFollowing = 5
    Nearest = 6