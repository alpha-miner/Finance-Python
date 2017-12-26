# -*- coding: utf-8 -*-
u"""
Created on 2016-12-21

@author: cheng.li
"""

import unittest
import numpy as np
import pandas as pd
from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingAverage
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingMin
from PyFin.Analysis.transformer import transform


class TestTransformer(unittest.TestCase):

    def test_transformer_with_category_name(self):
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 1, 2, 3],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2],
                               dtype=float)

        expression = SecurityMovingMax(2, 'b') + SecurityMovingMin(2, 'c')
        calculated = transform(test_df, [expression], cols=['user_factor'], category_field='code')
        expected = [13., 13., 13., 13., 11., 9, 9.]

        np.testing.assert_array_almost_equal(calculated['user_factor'], expected)

    def test_transformer_without_category_name(self):
        test_df = pd.DataFrame({'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 2, 3, 4, 5, 6, 7],
                               dtype=float)

        expression = SecurityMovingMax(20, 'b') + SecurityMovingMin(20, 'c')
        calculated = transform(test_df, [expression], cols=['user_factor'])
        expected = [13., 13., 13., 13., 12., 11., 10.]

        np.testing.assert_array_almost_equal(calculated['user_factor'], expected)

    def test_transformer_with_multiple_expression(self):
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 1, 2, 3],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2],
                               dtype=float)

        expression1 = SecurityMovingMax(20, 'b')
        expression2 = SecurityMovingMin(20, 'c')
        expression3 = SecurityMovingMax(20, 'b') + SecurityMovingMin(20, 'c')

        calculated = transform(test_df,
                               [expression1, expression2, expression3],
                               cols=['factor1', 'factor2', 'factor3'],
                               category_field='code')

        expected = [13., 13., 13., 13., 11., 9, 9.]

        np.testing.assert_array_almost_equal(calculated['factor3'], expected)
        np.testing.assert_array_almost_equal(calculated['factor1'] + calculated['factor2'], calculated['factor3'])

    def test_transformer_with_multiple_mixed_expression(self):
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 1, 2, 3],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2],
                               dtype=float)

        expression1 = 'b'
        expression2 = SecurityMovingMax(20, 'b') + SecurityMovingMin(20, 'c')

        calculated = transform(test_df,
                               [expression1, expression2],
                               cols=['b', 'factor2'],
                               category_field='code')

        expected = [13., 13., 13., 13., 11., 9, 9.]

        np.testing.assert_array_almost_equal(calculated['b'], test_df['b'])
        np.testing.assert_array_almost_equal(calculated['factor2'], expected)

    def test_transformer_with_category_group_totally_different(self):
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 5, 6, 7],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2],
                               dtype=float)

        expression = SecurityMovingAverage(2, 'b')
        calculated = transform(test_df,
                               [expression],
                               cols=['ma'],
                               category_field='code')

        expected = [4., 5., 6., 7., 6., 5., 4.]
        np.testing.assert_array_almost_equal(calculated['ma'], expected)

    def test_transformer_with_filter_value_holder(self):
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 1, 2, 3],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2],
                               dtype=float)

        value_holder = SecurityLatestValueHolder('b')
        filter = SecurityLatestValueHolder('b') >= 5

        filtered_value_holder = value_holder[filter]

        calculated = transform(test_df,
                               [filtered_value_holder],
                               cols=['filtered_b'],
                               category_field='code')

        self.assertTrue(np.all(calculated['filtered_b'] >= 5))
        expected = test_df[test_df.b >= 5]
        np.testing.assert_array_almost_equal(expected.b, calculated['filtered_b'])
        np.testing.assert_array_almost_equal(expected.code, calculated['code'])

    def test_transformer_with_category_value(self):
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 1, 2, 3],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2],
                               dtype=float)

        value_holder = SecurityLatestValueHolder('b')
        filter = SecurityLatestValueHolder('b') >= 5

        filtered_value_holder = value_holder[filter]

        calculated = transform(test_df,
                               [filtered_value_holder],
                               cols=['filtered_b'],
                               category_field='code')

        self.assertTrue(np.all(calculated['filtered_b'] >= 5))
        expected = test_df[test_df.b >= 5]
        np.testing.assert_array_almost_equal(expected.b, calculated['filtered_b'])
        np.testing.assert_array_equal(expected.code, calculated['code'])

    @staticmethod
    def test_transformer_with_category_for_comparing():
        test_df = pd.DataFrame({'code': [1, 2, 3, 4, 1, 2, 3],
                                'b': [4, 5, 6, 7, 6, 5, 4],
                                'c': [9, 8, 7, 6, 5, 4, 3]},
                               index=[1, 1, 1, 1, 2, 2, 2],
                               dtype=float)

        value_holder = SecurityLatestValueHolder('b') > 4.
        calculated = transform(test_df,
                               [value_holder],
                               cols=['filter'],
                               category_field='code')
        expected = [0., 1., 1., 1., 1., 1., 0.]
        np.testing.assert_array_almost_equal(expected, calculated['filter'])
