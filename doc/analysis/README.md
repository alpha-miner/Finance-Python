# Analysis

### 功能

跟踪在时间序列中，不同**符号**（*symbol*）关于某个**依赖**（*dependency*）的**运算**（*transform*）

* 执行指标的算术运算；
* 跟踪符号的依赖；
* 实现类似于移动窗口的功能；
* 可以进行复合运算。

### 基本使用

可以从``api``模块一下直接使用：

```python
In [1]: from PyFin import api
```

这里我们使用移动平均值作为例子：

```python
In [2]: value_holder = api.MA(2, 'x')
```

这里依赖是``'x'``，运算是``MA``（Moving Average），窗口长度是2。下面我们向``value_holder``中输入值(``push``):

```python
In [3]: value_holder.push({'s1': {'x': 2}})
```

这时我们可以通过``value``方法获取当前的运算结果：

```python
In [4]: value_holder.value
Out[4]:
s1    2.0
dtype: float64
```

我们可以继续输入值：

```python
In [6]: value_holder.push({'s1': {'x': 3}})
```

继续获取计算值：

```python
In [6]: value_holder.value
Out[6]:
s1 2.5
dtype: float64
```

我们仍然可以继续：

```python
In [7]: value_holder.push({'s1': {'x': 4}})
```

这个时候获取的值，就是最近的窗口移动平均

```python
In [8]: value_holder.value
Out[8]:
s1 3.5
dtype: float64
```

