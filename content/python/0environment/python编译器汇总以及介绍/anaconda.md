我们似乎总绕不开anaconda，因为很多资料或教程中总建议或者使用anaconda，其实不用该工具也可以实现数据分析与机器学习等内容，比如在我的一篇专栏文章中《6个套路入门ML：用鸢尾花data建立python机器学习的初步印象(一)》(https://zhuanlan.zhihu.com/p/26802995) ，不过在此之前先要安装很多与数据相关的模块包，如Numpy, Scipy，matplotlib，pandas，sklearn等等。有些包在python3.X的版本下还不好装(具体见我的《6个套路入门ML》文章有一些介绍)，这就需要有一个集成的管理工具，让我们把与数据分析有关的包安装好，省去了过多的麻烦。

(1)为什么安装anaconda？

Anaconda不是语言，它只是python的一个集成管理工具或系统，它把python做相关数据计算与分析所需要的包都集成在了一起，我们只需要安装Anaconda软件就行了，其它什么都不用装，包括python软件。Anaconda则是一个打包的集合，里面包含了720多个数据科学相关的开源包，在数据可视化、机器学习、深度学习等多方面都有涉及。不仅可以做数据分析，甚至可以用在大数据和人工智能领域。另外，安装它后就默认安装了python、IPython、Jupyter notebook和集成开发环境 Spyder等等。

总之一句话，安装anaconda让我们省去了大量下载模块包的时间，更加方便。

关于anaconda的安装与使用，目前网上的资料很多，在这里不过多介绍，只是说一两个关键的问题。

(2)anaconda的版本问题：选择python2.7还是3.6?

由于Python有2和3两个版本，因此Anaconda也在Python2和Python3的基础上推出了两个发行版，即Anaconda2和Anaconda3。Python3 被越来越多的开发者所接受，同时让人尴尬的是很多遗留的老系统依旧运行在 Python2 的环境中，因此有时你不得不同时在两个版本中进行开发，调试。

如何在系统中同时共存 Python2 和 Python3 是开发者不得不面对的问题，一个利好的消息是，Anaconda 能完美解决Python2 和 Python3 的共存问题。

conda 是 Anaconda 下用于包管理和环境管理的命令行工具，是 pip 和 vitualenv 的组合。安装成功后 conda 会默认加入到环境变量中，因此可直接在命令行窗口运行 conda 命令

如果你熟悉 virtualenv，那么上手 conda 非常容易，不熟悉 virtulenv 的也没关系，它提供的命令就几个，非常简单。我们可以利用 conda 的虚拟环境管理功能在 Python2 和 Python3 之间自由切换。

多版本切换

# 基于 python3.6 创建一个名为test_py3 的环境

conda create --name test_py3 python=3.6

# 基于 python2.7 创建一个名为test_py2 的环境

conda create --name test_py2 python=2.7

# 激活 test 环境

activate test_py2 # windows

source activate test_py2 # linux/mac

# 切换到python3

activate test_py3

更多命令，可查看帮助 conda -h

(3)anaconda自带了一款编辑器spyder与pycharm的比较

相比较而言，个人认为pycharm用起来更便捷，虽然spyder中所有的变量也都能显示，方便调试，里边还有ipython notebook，但是很细节的一些代码写作还是pycharm更便捷一些，比如引号””，spyder貌似无自动匹配机制，输入一个引号还需输入另一个引号。

强烈推荐anaconda+pycharm组合，因为anaconda安装的时候已经默认为你安装了一大堆做数据分析常用的包，所以，直接在pycharm中把默认解释器改为anaconda中的python即可(在pycharm-》settings-》Project Interpreter里找到要改环境的项目，选中，然后右上侧点击齿轮，Add local, 选刚才新建环境里的python.exe , 我的在 C:\Anaconda2\envs\tensorflow\python.exe， 之后确认即可)。

另外，只是针对数据分析与机器学习，anaconda用起来更方便一些，对于python的其他用途，比如爬虫、web开发，pycharm更好一些。针对大型的web框架修改调试，还是需要个大型IDE。

相关资料:https://blog.csdn.net/weixin_39815600/article/details/111024577