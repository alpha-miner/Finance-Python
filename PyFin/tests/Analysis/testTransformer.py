# -*- coding: utf-8 -*-
u"""
Created on 2016-12-21

@author: cheng.li
"""

import unittest
import numpy as np
import pandas as pd
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingMinimum
from PyFin.Analysis.transformer import transform


class TestTransformer(unittest.TestCase):

    def test_transformer_with_category_name(self):
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 1, 2, 3],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2])

        expression = SecurityMovingMax(20, 'b') + SecurityMovingMinimum(20, 'c')
        calculated = transform(test_df, [expression], cols=['user_factor'], category_field='code')
        expected = [13., 13., 13., 13., 11., 9, 9.]

        np.testing.assert_array_almost_equal(calculated['user_factor'], expected)

    def test_transformer_without_category_name(self):
        test_df = pd.DataFrame({'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2])

        expression = SecurityMovingMax(20, 'b') + SecurityMovingMinimum(20, 'c')
        calculated = transform(test_df, [expression], cols=['user_factor'])
        expected = [13., 13., 13., 13., 10., 10., 10.]

        np.testing.assert_array_almost_equal(calculated['user_factor'], expected)