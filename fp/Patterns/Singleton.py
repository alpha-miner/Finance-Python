# -*- coding: utf-8 -*-
u"""
Created on 2015-8-17

The implementation refers to this thread:
http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

@author: cheng.li
"""


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if 'forcedBuild' in kwargs and kwargs['forcedBuild']:
            return super(_Singleton, cls).__call__(*args, **kwargs)
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton('SingletonMeta', (object,), {})):
    pass
