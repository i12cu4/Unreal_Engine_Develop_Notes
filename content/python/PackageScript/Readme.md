# Compressed package operation by python

## Compressed package conversion/Add, Delete, Modify, query/Encryption and decryption

### 7Z - Code mainly running operations related to 7Z compressed packages
- Encrypt
- Anomaly detection
- Decryption
- Convert to RAR compressed package (including progress bar)

### RAR - Code mainly running operations related to RAR compressed packages
- File existence detection (printable csv)
- Encrypt
- Anomaly detection
- Decryption
- Unzip the files in the compressed package (taking jpg/png as an example)
- Delete specified files and folders (WinRar command mode,Rar command mode, hybrid mode)
  - Hybrid mode: Quickly detect with Rar commands, extract and process with WinRar commands, then compress and overwrite the file, and display UI(csv can be printed)
  - WinRar command mode: Use the WinRar command to extract and then compress and overwrite the file, and display the UI(default background execution).
  - Rar command Safe mode: Use the low-level Rar command to extract the files first and then compress and overwrite them
  - Rar Command Quick Mode: Using the low-level commands of Rar, it will be processed directly in the compressed package (csv can be printed).
- Secondary compression detection of compressed packages

### ZIP - Code mainly running operations related to ZIP compressed packages
- Encrypt
- Decryption
- Convert to RAR compressed package (including progress bar)

### More

Note 0: Before scheduling the code, make sure you have configured environments such as "WinRar", "7-Zip", "Python3", etc. in the device.

Note 1: The author did not place WinRar and 7Z in the Path configuration environment (Sysdm.cpl), so python was used to schedule the absolute path instead.

Note 2: The author installed WinRar and 7Z in the path **C:\Program File**. Note that it was File, not the system default file **C:\Program Files**.

Note 3: When you attempt to read the compressed package using code (decrypt the code), please ensure that the compressed package is not encrypted; otherwise, the reading may get stuck. (At this point, simply terminating the code is ineffective. You still need to use the Task manager to kill the process. Refer to the "Associated Handle" in "Resource Monitor".)

Note 4: The author did not further expand the functional areas of 7Z and ZIP because the author believes that RAR takes into account stability, compatibility, and the speed of pressurization and decompression compared to ZIP and 7Z. Therefore, it is chosen to convert the target compressed package to RAR before subsequent processing. The current script is sufficient for the author to use. If you have more operational requirements for ZIP and 7Z, you are welcome to supplement the code.

Note 5: Some programs may make operational changes to files (this is irreversible). If you want to achieve your goal, please make backups or conduct tests in advance. The author cannot guarantee that all programs will meet the expectations of users. Even though the author has used a large number of test samples, please operate with caution

## 压缩包转换/增删改查/加密解密

### 7Z - 主要运行7Z压缩包相关操作的代码
- 加密
- 异常检测
- 解密
- 转为RAR压缩包(含进度条)

### RAR - 主要运行RAR压缩包相关操作的代码
- 文件存在检测(可打印csv)
- 加密
- 异常检测
- 解密
- 解压压缩包中文件(jpg/png为例)
- 删除指定文件和文件夹(WinRar指令模式,Rar指令模式,混合模式)
    - 混合模式:以Rar指令快速检测,以WinRar指令将解压处理后再压缩覆盖文件,显示UI(可打印csv)
    - WinRar指令模式:使用WinRar指令,将解压处理后再压缩覆盖文件,显示UI(默认后台执行)
    - Rar指令安全模式:使用Rar底层指令,将解压处理后再压缩覆盖文件
    - Rar指令快速模式:使用Rar底层指令,将直接在压缩包中处理(可打印csv)
- 压缩包二次压缩检测

### ZIP - 主要运行ZIP压缩包相关操作的代码
- 加密
- 解密
- 转为RAR压缩包(含进度条)

### 更多...

注意0,在调度代码前,确保你已经在设备中配置"WinRar" "7-Zip" "Python3"等环境

注意1,笔者没有将WinRar以及7Z放到Path配置环境中(Sysdm.cpl),因而是使用python调度绝对路径来调度

注意2,笔者将WinRar以及7Z安装到了路径**C:\Program File**中,注意是File,不是系统默认文件**C:\Program Files**

注意3,当你尝试使用代码读取压缩包时(除解密代码),请确认该压缩包没有加密,否则可能会读取卡住(这个时候你单纯中止代码是无效的,你仍需要使用任务管理器将进程杀掉,参考"资源监视器"的"关联句柄")

注意4,笔者没有继续拓展7Z以及ZIP的功能区,因为笔者认为RAR相较ZIP和7Z兼顾了稳定性兼容性以及加压解压速度.因此选择将目标压缩包转为RAR后再做后续处理,目前的脚本对笔者来说是足够使用的.倘若你有对ZIP和7Z更多的操作需求,欢迎补充代码

注意5,有些程序会对文件进行操作改动(这是不可逆的),如果要实现目标请做好备份或者事先测试,笔者不保证所有程序都能符合使用者的期望,尽管笔者已经使用大量测试样本,请务必谨慎操作

### 更更多...

笔者在其他库扩展了7Z和winRAR的便携式(化二进制存于代码)的方案,详见[这里](https://github.com/i12cu4/PortableExecutableFile)

例如[转RAR(python程序)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E7%9B%AE%E6%A0%87%E6%BA%90%E4%BB%A3%E7%A0%81/%E8%BD%ACRAR.py) [转RAR(exe程序)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E6%89%93%E5%8C%85%E7%BB%93%E6%9E%9C/%E8%BD%ACRAR.exe)

可将若干文件和文件夹复选后拖动到该py/exe文件,将自行执行7z/zip转化为rar的程序(非7z/zip格式将会跳过执行),倘若是文件夹则会遍历子文件执行同样功能

例如[压缩包解压(python程序)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E7%9B%AE%E6%A0%87%E6%BA%90%E4%BB%A3%E7%A0%81/%E5%8E%8B%E7%BC%A9%E5%8C%85%E8%A7%A3%E5%8E%8B.py) [压缩包解压(exe程序)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E6%89%93%E5%8C%85%E7%BB%93%E6%9E%9C/%E5%8E%8B%E7%BC%A9%E5%8C%85%E8%A7%A3%E5%8E%8B.exe)

可将若干文件和文件夹复选后拖动到该py/exe文件,将自行执行7Z/zip/rar的解压功能(非7z/zip/rar格式将会跳过),倘若是文件夹则会遍历子文件执行同样功能

更多方案不在此继续赘述