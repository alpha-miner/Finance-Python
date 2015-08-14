# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

import math
import numpy as np


def norm(values, h):
    values = np.square(values)
    total = h * (np.sum(values) - 0.5 * values[0] - 0.5 * values[-1])
    return math.sqrt(total)
