import os
import subprocess
import sys
import shutil
import datetime

# 配置需要排除的文件/文件夹列表（支持通配符）
EXCLUDE_LIST = [
    ".vs",
    ".svn",
    "Binaries",
    "DerivedDataCache",
    "Intermediate",
    "PK",
    "Saved",
    "Build",
    "Platforms",
    "*.rar"
]
# 如果还需排除其他文件如RAR，可以添加如'*.rar'到列表中

import os
import subprocess
import sys
import shutil
import datetime

def find_rar_exe():
    # 检查常见Windows安装路径
    if sys.platform == 'win32':
        winrar_paths = [
            r"C:\Program File\WinRAR\Rar.exe"
        ]
        for path in winrar_paths:
            if os.path.exists(path):
                return path
    # 检查环境变量中的rar
    return shutil.which('rar')

def generate_timestamp():
    now = datetime.datetime.now()
    return f"{now.year}{now.month:02}{now.day}{now.hour:02}{now.minute:02}"

def main():
    current_dir = os.getcwd()
    dir_name = os.path.basename(current_dir)
    timestamp = generate_timestamp()

    base_name = f"{dir_name}_{timestamp}.rar"
    target_name = base_name

    rar_exe = find_rar_exe()
    if not rar_exe:
        print("错误：未找到RAR可执行文件。请安装WinRAR并确保其在PATH环境变量中。")
        input("按Enter键退出...")
        sys.exit(1)

    # 构建排除参数
    exclude_args = []
    for pattern in EXCLUDE_LIST:
        exclude_args.append(f'-x{pattern}')

    cmd = [rar_exe, 'a', '-r'] + exclude_args + [target_name, '.']

    try:
        subprocess.run(cmd, check=True, cwd=current_dir)
    except subprocess.CalledProcessError as e:
        print(f"压缩过程中发生错误：{e}")
        input("按Enter键退出...")
        sys.exit(1)

    print(f"压缩完成，文件保存为：{target_name}")
    print("\n操作执行完毕，窗口将在10秒后自动关闭...")
    os.system("timeout /t 10 /nobreak >nul")  # 仅Windows生效

if __name__ == "__main__":
    main()