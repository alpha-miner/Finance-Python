# -*- coding: utf-8 -*-
u"""
Created on 2017-1-30

@author: cheng.li
"""

from PyFin.Enums._DateGeneration cimport DateGeneration as dg


cpdef enum DateGeneration:
    Zero = dg.Zero
    Backward = dg.Backward
    Forward = dg.Forward