# -*- coding: utf-8 -*-
u"""
Created on 2015-10-22

@author: cheng.li
"""

import copy
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder
from PyFin.Math.Accumulators import Latest


class SecurityStatelessSingleValueHolder(SecurityValueHolder):
    def __init__(self, HolderType, dependency='x', symbolList=None):
        super(SecurityStatelessSingleValueHolder, self).__init__(dependency, symbolList)

        if isinstance(dependency, SecurityValueHolder):
            self._symbolList = dependency.symbolList
            self._dependency = dependency._dependency
            self._innerHolders = \
                {
                    name: HolderType(copy.deepcopy(dependency.holders[name])) for name in self._symbolList
                    }

        else:
            self._innerHolders = \
                {
                    name: HolderType(self._dependency) for name in self._symbolList
                    }


class SecurityLatestValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityLatestValueHolder, self).__init__(Latest, dependency, symbolList)

