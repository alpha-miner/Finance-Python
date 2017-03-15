# Work with Pandas

## 数据准备

```python
In [1]: from PyFin.examples.datas import sample_data
In [2]: sample_data
Out[2]:
            code  open  close
2016-01-01     1   2.0    1.7
2016-01-01     2   1.0    1.6
2016-01-02     1   1.5    0.9
2016-01-02     2   3.0    3.8
2016-01-03     1   2.4    1.6
2016-01-03     2   3.5    2.1
```

## 构造指标

这里我们就计算各个不同``code``的``'close'``的2日平均值：

```python
In [3]: from PyFin.api import MA
In [4]: ts = MA(2, 'close')
```

## 指标计算

这时我们可以将指标作用于感兴趣的数据之上，只需要调用``SecurityValueHolder``的``transform``方法：

```python
In [5]: ts.transform(sample_data, name='ma_2', category_field='code')
Out[5]:
            ma_2  code
2016-01-01  1.70     1
2016-01-01  1.60     2
2016-01-02  1.30     1
2016-01-02  2.70     2
2016-01-03  1.25     1
2016-01-03  2.95     2
```

## 参数的含义

在``transform``方法中，我们需要关注两个参数：``name``, ``category_field``:

* ``name``：转换后的结果所在列名，如果不填，则会给一个默认的列名；
* ``category_field``：代表``symbol``的列名，上面的结果中，我们是使用``'code'``列

我们也可以不输入``category_field``，那么在上面的计算，就会得到``'close'``列的滚动窗口为2的平均（注意，这个时候不是滚动窗口为2日的平均。因为原始数据中，每天有两个数据点，分别对应不同的``'code'``）：

```python
In [6]: ts = MA(2, 'close')
In [7]: ts.transform(sample_data, name='ma_2_no_code')
Out[7]:
            ma_2_no_code
2016-01-01          1.70
2016-01-01          1.65
2016-01-02          1.25
2016-01-02          2.35
2016-01-03          2.70
2016-01-03          1.85
```