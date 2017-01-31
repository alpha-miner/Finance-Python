# -*- coding: utf-8 -*-
u"""
Created on 2017-1-30

@author: cheng.li
"""

from PyFin.Enums._Weekdays cimport Weekdays as ws

cpdef enum Weekdays:
    Sunday = ws.Sunday
    Monday = ws.Monday
    Tuesday = ws.Tuesday
    Wednesday = ws.Wednesday
    Thursday = ws.Thursday
    Friday = ws.Friday
    Saturday = ws.Saturday