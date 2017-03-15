# Advances

## 四则运算加法

几乎所有的``Analysis``下的算符都支持四则运算，用户可以像书写数学公式一样写表达式：

```python
multiply_expression = expression1 * expression2
divided_expression = expression1 / expression2
added_expression = expression1 + expression2
subbed_expression = expression1 - expression2
```

## 复合运算

大部分的算符也可以支持复合运算，即：

```python
compounded_expression = expression(expression1)
```

## 条件表达式

表达式还可以根据另外的表达式结果过滤用户不关心的值：

```python
filtered_expression = expression1[expression2]
```