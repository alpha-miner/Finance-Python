# -*- coding: utf-8 -*-
u"""
Created on 2017-1-30

@author: cheng.li
"""

from PyFin.Enums._BizDayConventions cimport BizDayConventions as bdc

cpdef enum BizDayConventions:
    Following = bdc.Following
    ModifiedFollowing = bdc.ModifiedFollowing
    Preceding = bdc.Preceding
    ModifiedPreceding = bdc.ModifiedPreceding
    Unadjusted = bdc.Unadjusted
    HalfMonthModifiedFollowing = bdc.HalfMonthModifiedFollowing
    Nearest = bdc.Nearest