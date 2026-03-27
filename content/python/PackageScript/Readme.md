## 压缩包转换/增删改查/加密解密

### 7Z - 主要运行7Z压缩包相关操作的代码
- 加密
- 异常检测
- 解密
- 转为RAR压缩包(含进度条)

### RAR - 主要运行RAR压缩包相关操作的代码
- 删除指定文件和文件夹(WinRar指令模式,Rar指令模式,混合模式)
- 图种
- 文件存在检测(可打印csv)
- 解压压缩包中文件(jpg/png为例)
- 压缩包前缀
- 导出层级
- 加密
- 异常检测
- 解密
- 压缩
- 压缩包二次压缩检测

### ZIP - 主要运行ZIP压缩包相关操作的代码
- 加密
- 解密
- 转为RAR压缩包(含进度条)

### More - 更多
- 检查密码锁是否存在(同时检查zip/rar/7z)

### 更多...

注意-1,所有程序的详细内容在对应文件夹的Readme中有详细表述不在此冗杂表达

注意0,在调度代码前,确保你已经在设备中配置"WinRar" "7-Zip" "Python3"等环境

注意1,笔者没有将WinRar以及7Z放到Path配置环境中(Sysdm.cpl),因而是使用python调度绝对路径来调度

注意2,笔者将WinRar以及7Z安装到了路径**C:\Program File**中,注意是File,不是系统默认文件**C:\Program Files**

注意3,当你尝试使用代码读取压缩包时(除解密代码),请确认该压缩包没有加密,否则可能会读取卡住(这个时候你单纯中止代码是无效的,你仍需要使用任务管理器将进程杀掉,参考"资源监视器"的"关联句柄")

注意4,笔者没有继续拓展7Z以及ZIP的功能区,因为笔者认为RAR相较ZIP和7Z兼顾了稳定性兼容性以及加压解压速度.因此选择将目标压缩包转为RAR后再做后续处理,目前的脚本对笔者来说是足够使用的.倘若你有对ZIP和7Z更多的操作需求,欢迎补充代码

注意5,有些程序会对文件进行操作改动(这是不可逆的),如果要实现目标请做好备份或者事先测试,笔者不保证所有程序都能符合使用者的期望,尽管笔者已经使用大量测试样本,请务必谨慎操作

注意6,该lib可能更新会有延迟,倘若你想访问实时最新内容,请访问我的[总库点击此处](https://github.com/i12cu4/Unreal_Engine_Develop_Notes/tree/main/content/python/PackageScript)

### 更更多...

笔者在其他库扩展了7Z和winRAR的便携式(化二进制存于代码)的方案,详见[这里](https://github.com/i12cu4/PortableExecutableFile)

例如[转RAR(python程序)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E7%9B%AE%E6%A0%87%E6%BA%90%E4%BB%A3%E7%A0%81/%E8%BD%ACRAR.py) [转RAR(exe程序)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E6%89%93%E5%8C%85%E7%BB%93%E6%9E%9C/%E8%BD%ACRAR.exe)

可将若干文件和文件夹复选后拖动到该py/exe文件,将自行执行7z/zip转化为rar的程序(非7z/zip格式将会跳过执行),倘若是文件夹则会遍历子文件执行同样功能

例如[压缩包解压(python程序)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E7%9B%AE%E6%A0%87%E6%BA%90%E4%BB%A3%E7%A0%81/%E5%8E%8B%E7%BC%A9%E5%8C%85%E8%A7%A3%E5%8E%8B.py) [压缩包解压(exe程序)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E6%89%93%E5%8C%85%E7%BB%93%E6%9E%9C/%E5%8E%8B%E7%BC%A9%E5%8C%85%E8%A7%A3%E5%8E%8B.exe)

可将若干文件和文件夹复选后拖动到该py/exe文件,将自行执行7Z/zip/rar的解压功能(非7z/zip/rar格式将会跳过),倘若是文件夹则会遍历子文件执行同样功能

更多方案不在此继续赘述