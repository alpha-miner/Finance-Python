# -*- coding: utf-8 -*-
u"""
Created on 2016-4-1

@author: cheng.li
"""

from enum import Enum
from enum import unique
import numpy as np
import pandas as pd
import scipy.optimize as opt
from PyFin.POpt.Calculators import calculate_annualized_return
from PyFin.POpt.Calculators import calculate_volatility
from PyFin.POpt.Calculators import calculate_sharp
from PyFin.POpt.Calculators import calculate_sortino
from PyFin.POpt.Calculators import calculate_max_drawdown
from PyFin.POpt.Calculators import calculate_mean_drawdown


def portfolio_returns(weights, nav_table, rebalance):
    if rebalance:
        return_table = np.log(nav_table.values[1:, :] / nav_table.values[:-1, :])
        returns = np.dot(return_table, weights) / sum(weights)
    else:
        final_nav = np.dot(nav_table, weights) / sum(weights)
        returns = np.log(final_nav[1:] / final_nav[:-1])
    return returns


def utility_calculator(returns, opt_type):
    # switch between different target types
    if opt_type == OptTarget.RETURN:
        return calculate_annualized_return(returns)
    elif opt_type == OptTarget.VOL:
        return -calculate_volatility(returns)
    elif opt_type == OptTarget.MAX_DRAWDOWN:
        return -calculate_max_drawdown(returns)
    elif opt_type == OptTarget.MEAN_DRAWDOWN:
        return -calculate_mean_drawdown(returns)
    elif opt_type == OptTarget.SHARP:
        return calculate_sharp(returns)
    elif opt_type == OptTarget.SORTINO:
        return calculate_sortino(returns)
    elif opt_type == OptTarget.RETURN_D_MAX_DRAWDOWN:
        return calculate_annualized_return(returns) / calculate_max_drawdown(returns)


@unique
class OptTarget(str, Enum):
    RETURN = 'RETURN'
    VOL = 'VOL'
    MAX_DRAWDOWN = 'MAX_DRAWDOWN'
    MEAN_DRAWDOWN = 'MEAN_DRAWDOWN'
    SHARP = 'SHARP'
    SORTINO = 'SORTINO'
    RETURN_D_MAX_DRAWDOWN = 'RETURN_D_MAX_DRAWDOWN'


def portfolio_optimization(weights, nav_table, opt_type, rebalance=False):
    if not rebalance and \
            (opt_type == OptTarget.SORTINO
             or opt_type == OptTarget.RETURN_D_MAX_DRAWDOWN
             or opt_type == OptTarget.MAX_DRAWDOWN):
        raise ValueError("Portfolio optimization target can't be set as "
                         "maximize sortino ratio"
                         "or minimize max draw down "
                         "or maximuze return to max draw down.")

    if opt_type == OptTarget.SORTINO or \
                    opt_type == OptTarget.RETURN or \
                    opt_type == OptTarget.VOL or \
                    opt_type == OptTarget.SHARP or \
                    opt_type == OptTarget.MEAN_DRAWDOWN or \
            (rebalance and (opt_type == OptTarget.MAX_DRAWDOWN or
                                   opt_type == OptTarget.RETURN_D_MAX_DRAWDOWN or
                                   opt_type == OptTarget.SORTINO)):
        x0 = weights

        bounds = [(0.0, 0.25) for _ in weights]

        def eq_cond(x, *args):
            return sum(x) - 1.0

        def func(weights):
            returns = portfolio_returns(weights, nav_table, rebalance)
            return -utility_calculator(returns, opt_type)

        out, fx, its, imode, smode = opt.fmin_slsqp(func=func,
                                                    x0=x0,
                                                    bounds=bounds,
                                                    eqcons=[eq_cond],
                                                    full_output=True,
                                                    iprint=-1,
                                                    acc=1e-12,
                                                    iter=300000)

        out = {col: weight for col, weight in zip(nav_table.columns, out)}
        return pd.DataFrame(out, index=['weight']), fx, its, imode, smode
