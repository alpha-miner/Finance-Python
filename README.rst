-------------

|Build Status| |Coverage Status| |Join the chat at https://gitter.im/wegamekinglc/algotrading|

-------------

finpy
====================

纯python实现的金融计算库，目标是提供进行量化交易必要的工具，包括但不限于：定价分析工具、技术分析指标。其中部分实现参考了quantlib。

依赖
-------------

::

  coverage
  enum34
  numpy
  pandas
  scipy

安装
-------------

首先将代码保存至本地：

::

  git clone https://github.com/ChinaQuants/Finance-Python.git (如果你是从github获取)
  cd finance-Python
  python setpy.py install


安装之后，可以直先接运行测试：

.. code:: python

  python setup.py test

版本历史
-------------

0.3.x
^^^^^^^^^^^^^

0.2.0
^^^^^^^^^^^^^

1. 实现了策略的风险收益指标计算；
2. 一些简单的期权计算公式。

0.1.0
^^^^^^^^^^^^^

基本的日期相关函数的实现。

.. |Build Status| image:: https://travis-ci.org/wegamekinglc/Finance-Python.svg?branch=master
   :target: https://travis-ci.org/wegamekinglc/Finance-Python
.. |Coverage Status| image:: https://coveralls.io/repos/wegamekinglc/Finance-Python/badge.svg?branch=master&service=github
   :target: https://coveralls.io/r/wegamekinglc/Finance-Python
.. |Join the chat at https://gitter.im/wegamekinglc/algotrading| image:: https://badges.gitter.im/Join%20Chat.svg
   :target: https://gitter.im/wegamekinglc/algotrading?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
