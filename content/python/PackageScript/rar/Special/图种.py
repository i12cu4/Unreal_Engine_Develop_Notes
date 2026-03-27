import subprocess

# 定义变量存储路径
source_png_path = 'C:\\Users\\i12cu84\\Desktop\\1.png'
source_rar_path = 'C:\\Users\\i12cu84\\Desktop\\2.rar'
destination_png_path = 'C:\\Users\\i12cu84\\Desktop\\3.png'

# 调用CMD指令
result = subprocess.run(['cmd.exe', '/c', 'copy /b ' + source_png_path + '+' + source_rar_path + ' ' + destination_png_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# 获取输出
stdout = result.stdout
stderr = result.stderr

print("标准输出：")
print(stdout)

print("标准错误：")
print(stderr)

# 检查指令是否成功执行
if result.returncode == 0:
    print("指令成功执行")
else:
    print("指令执行错误")

"""
| 操作 | 结果 |
|------|------|
| 用看图软件打开 `3.png` | ✅ 正常显示原图（附加内容被忽略） |
| 用 WinRAR/7-Zip 打开 `3.png` | ✅ 能解压出 `2.rar` 里的所有文件 |
| 查看文件大小 | 📏 = `1.png` 大小 + `2.rar` 大小 |
| 重命名为 `3.rar` 后解压 | ✅ 同样能解压出隐藏内容 |
"""