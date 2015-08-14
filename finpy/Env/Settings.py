# -*- coding: utf-8 -*-
u"""
Created on 2015-8-14

@author: cheng.li
"""

from finpy.Patterns.ClassProperty import ClassPropertyMetaClass
from finpy.Patterns.ClassProperty import classproperty
from finpy.DateUtilities import Date


class Settings(object):
    __metaclass__ = ClassPropertyMetaClass
    _evaluationDate = Date.todaysDate()

    @classproperty
    def evaluationDate(cls):
        return cls._evaluationDate

    @evaluationDate.setter
    def evaluationDate(cls, value):
        if not isinstance(value, Date):
            raise ValueError("{0} is not a valid finpy date object".format(value))
        cls._evaluationDate = value
