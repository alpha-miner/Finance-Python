# -*- coding: utf-8 -*-
u"""
Created on 2019-2-16

@author: cheng.li
"""

import os
from PyFin.api import *
from alphamind.api import *


universe_name = 'zz1000'
formula = CSBottomN(LAST('ROE'), 20)
ref_date = '2019-02-13'

depends = formula.fields

engine = SqlEngine(os.environ['DB_URI'])
universe = Universe(universe_name)
codes = universe.query(engine, dates=[ref_date])

factors = engine.fetch_factor(ref_date, depends, codes.code.tolist())
factors.index = [1] * len(factors)
factors = factors[['code'] + depends]

res = formula.transform(factors, name='factor', category_field='code')

print(res[res.factor == 1])
