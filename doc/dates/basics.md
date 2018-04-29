# basics

## 如何使用

所有的公开`api`都在`PyFin.api`模块下：

```python
In [1]: from PyFin.api import *
```

## 测试日期

在某工作日历下，是否为工作日：

```python
In [2]: isBizDay('china.sse', '2017-03-19')
Out[2]: False
```

## 生成日期序列

生成区间内的所有日期:

```python
In [3]: datesList('2017-01-01', '2017-01-15')
Out[3]:
[datetime.datetime(2017, 1, 1, 0, 0),
 datetime.datetime(2017, 1, 2, 0, 0),
 datetime.datetime(2017, 1, 3, 0, 0),
 datetime.datetime(2017, 1, 4, 0, 0),
 datetime.datetime(2017, 1, 5, 0, 0),
 datetime.datetime(2017, 1, 6, 0, 0),
 datetime.datetime(2017, 1, 7, 0, 0),
 datetime.datetime(2017, 1, 8, 0, 0),
 datetime.datetime(2017, 1, 9, 0, 0),
 datetime.datetime(2017, 1, 10, 0, 0),
 datetime.datetime(2017, 1, 11, 0, 0),
 datetime.datetime(2017, 1, 12, 0, 0),
 datetime.datetime(2017, 1, 13, 0, 0),
 datetime.datetime(2017, 1, 14, 0, 0),
 datetime.datetime(2017, 1, 15, 0, 0)]
```

生成区间内所有的工作日：

```python
In [4]: bizDatesList('china.sse', '2017-01-01', '2017-01-15')
Out[4]:
[datetime.datetime(2017, 1, 3, 0, 0),
 datetime.datetime(2017, 1, 4, 0, 0),
 datetime.datetime(2017, 1, 5, 0, 0),
 datetime.datetime(2017, 1, 6, 0, 0),
 datetime.datetime(2017, 1, 9, 0, 0),
 datetime.datetime(2017, 1, 10, 0, 0),
 datetime.datetime(2017, 1, 11, 0, 0),
 datetime.datetime(2017, 1, 12, 0, 0),
 datetime.datetime(2017, 1, 13, 0, 0)]
```

生成区间内所有的节假日：

```python
In [5]: holDatesList('china.sse', '2017-01-01', '2017-01-15')
Out[5]:
[datetime.datetime(2017, 1, 1, 0, 0),
 datetime.datetime(2017, 1, 2, 0, 0),
 datetime.datetime(2017, 1, 7, 0, 0),
 datetime.datetime(2017, 1, 8, 0, 0),
 datetime.datetime(2017, 1, 14, 0, 0),
 datetime.datetime(2017, 1, 15, 0, 0)]
```

## 调整日期

按照日历日调整日期：

```python
In [6]: advanceDate('2017-03-19', '3m')
Out[6]: datetime.datetime(2017, 6, 19, 0, 0)
```

也可以向前调整：

```python
In [7]: advanceDate('2017-03-19', '-3d')
Out[7]: datetime.datetime(2017, 3, 16, 0, 0)
```

可以按照工作日调整日期，忽略掉节假日：

```python
In [8]: advanceDateByCalendar('china.sse', '2017-03-17', '1d', convention=BizDayConventions.Following)
Out[8]: datetime.datetime(2017, 3, 20, 0, 0)
```

## 生成日程序列

可以按照固定的频率生成日程表，下面的代码按照月度频率生成交易日：

```python
In [9]: makeSchedule('2017-01-01', '2017-12-31', '1m', 'china.sse')
Out[9]:
[datetime.datetime(2017, 1, 3, 0, 0),
 datetime.datetime(2017, 2, 3, 0, 0),
 datetime.datetime(2017, 3, 1, 0, 0),
 datetime.datetime(2017, 4, 5, 0, 0),
 datetime.datetime(2017, 5, 2, 0, 0),
 datetime.datetime(2017, 6, 1, 0, 0),
 datetime.datetime(2017, 7, 3, 0, 0),
 datetime.datetime(2017, 8, 1, 0, 0),
 datetime.datetime(2017, 9, 1, 0, 0),
 datetime.datetime(2017, 10, 9, 0, 0),
 datetime.datetime(2017, 11, 1, 0, 0),
 datetime.datetime(2017, 12, 1, 0, 0),
 datetime.datetime(2018, 1, 1, 0, 0)]
```
