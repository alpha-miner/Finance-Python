# -*- coding: utf-8 -*-
u"""
Created on 2016-4-1

@author: cheng.li
"""

import math
from PyFin.Math.Accumulators import MovingSharp
from PyFin.Math.Accumulators import MovingSortino
from PyFin.Math.Accumulators import MovingMaxDrawdown
from PyFin.Math.Accumulators import MovingAverageDrawdown


def calculate_annualized_return(returns):
    return returns.mean() * 50


def calculate_volatility(returns):
    return returns.std(ddof=1) * math.sqrt(50)


def calculate_max_drawdown(returns):
    mdrawdown = MovingMaxDrawdown(len(returns))
    for ret in returns:
        mdrawdown.push({'ret': ret})
    return -mdrawdown.value[0]


def calculate_mean_drawdown(returns):
    mdrawdown = MovingAverageDrawdown(len(returns))
    for ret in returns:
        mdrawdown.push({'ret': ret})
    return -mdrawdown.value[0]


def calculate_sharp(returns):
    msharp = MovingSharp(len(returns))
    for ret in returns:
        msharp.push({'ret': ret, 'riskFree': 0.})
    return msharp.value * math.sqrt(50)


def calculate_sortino(returns):
    msortino = MovingSortino(len(returns))
    for ret in returns:
        msortino.push({'ret': ret, 'riskFree': 0.})
    return msortino.value * math.sqrt(50)