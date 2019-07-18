from PyFin.api import *
from sqlalchemy import select, create_engine, and_
import pandas as pd
from alphamind.data.dbmodel.models import Market

engine = create_engine('postgresql+psycopg2://alpha:alpha@180.166.26.82:8889/alpha')
begin_date = '2018-12-26'
end_date = '2018-12-28'
query = select([Market]).where(
    and_(Market.trade_date >= begin_date, Market.trade_date <= end_date, ))
mkt_df = pd.read_sql(query, engine)
mkt_df.rename(columns={'preClosePrice': 'pre_close', 'openPrice': 'openPrice',
                       'highestPrice': 'highestPrice', 'lowestPrice': 'lowestPrice',
                       'closePrice': 'closePrice', 'turnoverVol': 'turnoverVol',
                       'turnoverValue': 'turnover_value', 'accumAdjFactor': 'accum_adj',
                       'vwap': 'vwap'}, inplace=True)
mkt_df = mkt_df[[('000000' + str(code))[-6:][0] in '036' for code in mkt_df['code']]]
trade_date_list = list(set(mkt_df.trade_date))
trade_date_list.sort(reverse=True)
mkt_df = mkt_df.sort_values(['trade_date', 'code']).set_index(['trade_date', 'code'])
mkt_df = mkt_df[mkt_df['turnoverVol'] > 0]

import datetime as dt

start = dt.datetime.now()

expression1 = LAST('closePrice') * 2 - LAST('lowestPrice') - LAST('highestPrice')
expression2 = LAST('highestPrice') - LAST('lowestPrice')

alpha2 = DIFF(expression1 / expression2) * - 1

df = mkt_df.loc['2018-12-26':'2018-12-28'].reset_index(level=1)
df['alpha2'] = alpha2.transform(df, name='alpha2', category_field='code')['alpha2']
#df[['trade_date', 'code', 'closePrice', 'highestPrice', 'lowestPrice', 'alpha2']].set_index('code').loc[603999]
print("elapsed time: {0}".format(dt.datetime.now() - start))
