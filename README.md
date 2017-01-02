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

### 依赖

    coverage
    cython
    enum34
    numpy
    pandas
    scipy
    
以及相关的c/c++编译器（例如Linux下的gcc，windows下的visual studio）

### 安装

首先将代码保存至本地：

    git clone https://github.com/ChinaQuants/Finance-Python.git (如果你是从github获取)
    cd finance-Python
    python setpy.py install


安装之后，可以直先接运行测试：

    python setup.py test
    
### 开发环境

在代码目录下，需要运行如下指令：

    python setup.py build_ext --inplace
    
如果是windows环境，可能需要显式的指定需要的编译器，例如选用Visual Studio的c/c++编译器：

    python setup.py build_ext --inplace --compiler=msvc


### 主要功能

* 可以实现复合运算的指标库，方便的与pandas结合；
* 基于日历的金融日期计算，包括在不同市场下的节假日安排；
* 资产组合优化函数（实验阶段，功能有限并且在未来可能会有大幅度修改）；
* 一些金融产品的定价模型（功能有限）。
