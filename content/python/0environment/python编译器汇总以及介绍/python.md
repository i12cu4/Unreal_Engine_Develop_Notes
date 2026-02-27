cmd -> py
    python -0p (获取py路径)
    python main.py (运行main.py文件)
    python -m pip install --upgrade pip (更新pip)
    python -m site (获取第三方库路径)
    where python (获取python路径)
    where pip (获取pip路径)








python -> coding
    exit() #退出python环境
    %run C:/main.py #运行main.py文件

```
import os
os.getcwd()#输出当前路径
```

```
import sys
print(sys.executable)#输出python解释器路径
```









pip -> coding
    pip install [lib] (下载库)
    pip install --upgrade [lib] (更新库)
    pip install --upgrade pip (更新pip)
    pip install --ignore-installed [lib] (处理下载中断问题)
    pip install [lib]==1.8.0 (指定版本安装)
    where pip (获取pip路径)
    pip install check (来检查spyder的依赖环境是否满足)
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple (设置python的依赖安装镜像服务器为清华大学服务器)
->Writing to C:\Users\chru\AppData\Roaming\pip\pip.ini
        清华大学： https://pypi.tuna.tsinghua.edu.cn/simple/
        阿里云： http://mirrors.aliyun.com/pypi/simple/
        中国科技大学： https://pypi.mirrors.ustc.edu.cn/simple/
        豆瓣： http://pypi.douban.com/simple/
        中国科学技术大学： http://pypi.mirrors.ustc.edu.cn/simple/
    pip install -r A.txt (读取A文本下载库)






anaconda -> coding
    conda install [lib] (下载库)
    conda update anaconda-navigator (升级navigator)
    anaconda-navigator --reset (重置navigator)
    conda update anaconda-client (升级客户端)
    conda update -f anaconda-client (升级安装依赖包)
    conda info --envs (查看所有环境)
    conda clean ... (清理pkgs缓存,参考内容https://zhuanlan.zhihu.com/p/190777953)
