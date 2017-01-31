# -*- coding: utf-8 -*-
u"""
Created on 2017-1-30

@author: cheng.li
"""

from PyFin.Enums._OptionType cimport OptionType as ot


cpdef enum OptionType:
    Call = ot.Call
    Put = ot.Put
