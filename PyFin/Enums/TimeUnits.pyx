# -*- coding: utf-8 -*-
u"""
Created on 2017-1-30

@author: cheng.li
"""

from PyFin.Enums._TimeUnits cimport TimeUnits as tu

cpdef enum TimeUnits:
    BDays = tu.BDays
    Days = tu.Days
    Weeks = tu.Weeks
    Months = tu.Months
    Years = tu.Years