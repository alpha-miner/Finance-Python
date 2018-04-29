# Advances

## 四则运算加法

几乎所有的``Analysis``下的算符都支持四则运算，用户可以像书写数学公式一样写表达式：

```python
multiply_expression = expression1 * expression2
divided_expression = expression1 / expression2
added_expression = expression1 + expression2
subbed_expression = expression1 - expression2
```

例如，我们可以计算``open``、``high``、``low``、``close``的均值：

```python
In [1]: price_average = (LAST('open') + LAST('high') + LAST('low') + LAST('close')) / 4.
```

上面的式子直观的定义了上面价格的均值。下面我们可以准备数据：

```python
In [2]: data = dict(aapl=dict(open=2., high=4., low=1., close=3.),
......:             ibm=dict(open=6., high=7., low=4., close=7.))
```

推送数据:

```python
In [3]:price_average.push(data)
```

获取结果：

```python
In [4]: price_average.value
Out[4]: SecurityValues({'aapl': 2.5, 'ibm': 6.0})
```

## 复合运算

大部分的算符也可以支持复合运算，即：

```python
compounded_expression = expression(expression1)
```

我们可以计算上面定义的均价的收益率：

```python
In [5]: simple_return = RETURNSimple(price_average)
```

同样的我们可以推送数据：

```python
In [6]: simple_return.push(data)

In [7]: simple_return.value
Out[7]: SecurityValues({'aapl': nan, 'ibm': nan})
```

从输出结果看到，我们还需要再推送一批数据，才能计算收益率。简单起见，我们仍然推送上一次的数据：

```python
In [8]: simple_return.push(data)

In [9]: simple_return.value
Out[9]: SecurityValues({'aapl': 0.0, 'ibm': 0.0})
```

显然的收益率为0.

## 条件表达式

表达式还可以根据另外的表达式结果过滤用户不关心的值：

```python
filtered_expression = expression1[expression2]
```

比如我们在上面的例子中，想过滤掉均价低于3的股票：

```python
In [10]: filter_flag = price_average > 3.

In [11]: filtered_value = price_average[filter_flag]
```

输出的结果：

```python
In [12]: filtered_value.push(data)

In [13]: filtered_value.value
Out[13]: SecurityValues({'ibm': 6.0})
```


## 一些特殊的算符

* ``IIF``

有些时候，用户过滤出满足某些条件的数据，并不是要删除它，而只是要更改这部分的值。例如，在上面的例子中，我们希望保留大于3的价格；对于低于3的均价，以0来代替。

上面的功能，我们可以通过以下的表达式实现：

```python
In [14]: masked_value = IIF(filter_flag, price_average, 0.)
```

```python
In [15]: masked_value.push(data)

In [16]: masked_value.value
Out[16]: SecurityValues({'aapl': 0.0, 'ibm': 6.0})
```



