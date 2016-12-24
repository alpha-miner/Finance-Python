# Finance - Python

<table>
<tr>
  <td>Latest Release</td>
  <td><img src="https://img.shields.io/pypi/v/finance-python.svg" alt="latest release" /></td>
</tr>
<tr>
  <td>Build Status</td>
  <td>
    <a href="https://travis-ci.org/wegamekinglc/Finance-Python">
    <img src="https://travis-ci.org/wegamekinglc/Finance-Python.svg?branch=master" alt="travis build status" />
    </a>
  </td>
</tr>
<tr>
  <td>Coverage</td>
  <td><img src="https://coveralls.io/repos/wegamekinglc/Finance-Python/badge.svg?branch=master&service=github" alt="coverage" /></td>
</tr>
</table>

纯python实现的金融计算库，目标是提供进行量化交易必要的工具，包括但不限于：定价分析工具、技术分析指标。其中部分实现参考了quantlib。

## 依赖

    coverage
    enum34
    numpy
    pandas
    scipy

## 安装


首先将代码保存至本地：

    git clone https://github.com/ChinaQuants/Finance-Python.git (如果你是从github获取)
    cd finance-Python
    python setpy.py install


安装之后，可以直先接运行测试：

    python setup.py test

版本历史
-------------

### 0.3.x


### 0.2.0

1. 实现了策略的风险收益指标计算；
2. 一些简单的期权计算公式。

### 0.1.0


基本的日期相关函数的实现。
