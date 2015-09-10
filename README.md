## finpy
-------------

纯python实现的金融计算库，目标是提供进行量化交易必要的工具，包括但不限于：定价分析工具、技术分析指标以及回测平台。其中部分实现参考了quantlib。

## 依赖
-------------

~~~
enum34 (python2)
numpy
scipy
pandas
~~~

## 安装
-------------

首先将代码保存至本地：

~~~
git clone https://github.com/ChinaQuants/Finance-Python.git (如果你是从github获取)
cd finance-Python
~~~

根据使用的python版本不同，例如Python2:

~~~
pip install -r requirements/python2.txt
python setpy.py install
~~~

对于python3：

~~~
pip install -r requirements/python3.txt
python setpy.py install
~~~

安装之后，可以直先接运行测试：
~~~
pip install -r requirements/test.txt
python setup.py test
~~~

## 版本历史
-------------

### 0.2.0

1. 实现了策略的风险收益指标计算；
2. 一些简单的期权计算公式。

### 0.1.0

基本的日期相关函数的实现。
