# Finance - Python

### 依赖

    coverage
    cython
    enum34
    numpy
    pandas
    scipy
    six
    
以及相关的c/c++编译器（例如Linux下的gcc，windows下的visual studio）

* 可选依赖

如果您在Windows上工作，并且想使用相关的Excel功能（请见根目录下``excel``文件夹），则需以下工具：

    xlwings

### 安装

1. 从最新源代码安装

    首先将代码保存至本地：
    
        git clone https://github.com/ChinaQuants/Finance-Python.git (如果你是从github获取)
        cd finance-Python
        
    * *Linux*
    
    只需运行如下命令：
    
        python setpy.py install
    
    * *Windows*
        
    需要修改项目根目录下``setup.cfg``文件，添加如下两行：
    
        [build]
        compiler=msvc
    
    然后再运行：``python setup.py install``
    
    安装之后，可以直先接运行测试：
    
        python setup.py test
        
2. 从``pypi``安装

    * *Linux*
    
    只需运行如下命令：
    
        pip install Finance-Python
        
    * *Windows*
    
    从编译完成的``.whl``文件安装：
    
        pip insall --use-wheel Finance-Python
        
    现阶段支持python 2.7, 3.5以及3.6版本，并且只有64位版本。如果在首次运行时遇到dll文件无法找到的问题，请确保您的电脑上有visual studio 2015的运行时环境，
    下载地址：[Visual C++ Redistributable for Visual Studio 2015](https://www.microsoft.com/en-us/download/details.aspx?id=48145)
    
    
### 开发环境

* *Linux*

在代码目录下，需要运行如下指令：

    python setup.py build_ext --inplace
    
* *Windows*
    
需要显式的指定编译器，例如选用Visual Studio的c/c++编译器：

    python setup.py build_ext --inplace --compiler=msvc
    
或者修改``setup.cfg``文件。


### 主要功能

* 可以实现复合运算的指标库，方便的与pandas结合；
* 基于日历的金融日期计算，包括在不同市场下的节假日安排；
* 资产组合优化函数（实验阶段，功能有限并且在未来可能会有大幅度修改）；
* 一些金融产品的定价模型（功能有限）。
