import os
import subprocess
import sys
import shutil
import datetime
import shlex

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

def find_rar_exe():
    """查找RAR可执行文件路径""" 
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
    """生成时间戳字符串，格式：YYYYMMDDHHMM"""
    now = datetime.datetime.now()
    return f"{now.year}{now.month:02}{now.day:02}{now.hour:02}{now.minute:02}"

def sanitize_filename(name):
    """清理文件名中的特殊字符，只保留安全字符"""
    # 移除括号等可能导致命令行解析问题的字符
    for char in '()[]{}<>|;&^%$#@!`':
        name = name.replace(char, '_')
    # 连续的下划线替换为单个下划线
    while '__' in name:
        name = name.replace('__', '_')
    # 移除首尾非字母数字字符
    name = name.strip('_-. ')
    return name

def compress_folder(folder_path, rar_exe, timestamp):
    """
    压缩单个文件夹
    :param folder_path: 要压缩的文件夹路径
    :param rar_exe: RAR可执行文件路径
    :param timestamp: 时间戳
    """
    try:
        # 确保路径是绝对路径
        folder_path = os.path.abspath(folder_path)
        if not os.path.isdir(folder_path):
            print(f"错误: 路径不是文件夹: {folder_path}")
            return False
            
        # 获取父目录和文件夹名
        parent_dir = os.path.dirname(folder_path)
        folder_name = os.path.basename(folder_path)
        
        # 清理文件夹名中的特殊字符（用于生成压缩包名）
        safe_folder_name = sanitize_filename(folder_name)
        
        # 生成压缩包名称
        rar_filename = f"{safe_folder_name}.rar"
        rar_filepath = os.path.join(parent_dir, rar_filename)
        
        # 构建排除参数（直接使用模式，不在前面添加文件夹名）
        exclude_args = []
        for pattern in EXCLUDE_LIST:
            exclude_args.append(f'-x{pattern}')
        
        # 构建RAR命令 - 使用列表格式，确保正确处理空格
        cmd = [rar_exe, 'a', '-r', '-ep1', '-y'] + exclude_args + [rar_filename, folder_name]
        
        print(f"正在压缩: {folder_name} -> {rar_filename}")
        
        # 在父目录执行命令
        result = subprocess.run(
            cmd,
            check=True,
            cwd=parent_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(f"成功创建: {rar_filepath}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"压缩失败 ({folder_name}):")
        print(f"错误代码: {e.returncode}")
        if e.stderr:
            print(f"错误输出:\n{e.stderr}")
        elif e.stdout:
            print(f"输出:\n{e.stdout}")
        return False
    except Exception as e:
        print(f"处理 {folder_path} 时发生意外错误: {str(e)}")
        return False

def get_dragged_folders():
    """获取拖放的文件夹路径，正确处理包含空格的路径"""
    # 在Windows上，当拖放文件夹时，sys.argv包含完整路径
    # 第一个参数是脚本自身，其余是拖放的项目
    if len(sys.argv) <= 1:
        return [os.getcwd()]  # 无参数时使用当前目录
    
    # 获取除脚本外的所有参数
    paths = sys.argv[1:]
    print(f"接收到的原始路径: {paths}")
    
    # 筛选出真实存在的文件夹
    valid_folders = []
    for path in paths:
        if os.path.isdir(path):
            valid_folders.append(path)
            print(f"识别到有效文件夹: {path}")
        else:
            print(f"跳过无效路径: {path}")
    
    # 调试：打印所有识别到的文件夹
    if valid_folders:
        print("\n将处理以下文件夹:")
        for folder in valid_folders:
            print(f"- {folder}")
        print("-" * 50)
    
    return valid_folders if valid_folders else [os.getcwd()]

def main():
    # 查找RAR可执行文件
    rar_exe = find_rar_exe()
    if not rar_exe:
        print("错误：未找到RAR可执行文件。请安装WinRAR并确保其在PATH环境变量中。")
        input("按Enter键退出...")
        sys.exit(1)
    
    # 生成统一的时间戳（同一批操作使用相同时间戳）
    timestamp = generate_timestamp()
    
    # 获取要处理的文件夹（正确处理拖放的文件夹）
    folders = get_dragged_folders()
    
    success_count = 0
    failure_count = 0
    
    print(f"\n开始压缩操作 (时间戳: {timestamp})")
    print("=" * 60)
    
    for folder in folders:
        if compress_folder(folder, rar_exe, ""):
            success_count += 1
        else:
            failure_count += 1
        print("=" * 60)
    
    # 总结报告
    print("\n压缩操作完成!")
    print(f"成功: {success_count} 个文件夹")
    print(f"失败: {failure_count} 个文件夹")
    
    if failure_count > 0:
        print("\n注意: 部分文件夹压缩失败，请检查上述错误信息")
    
    print("\n操作执行完毕，窗口将在1秒后自动关闭...")
    if sys.platform == 'win32':
        os.system("timeout /t 1 /nobreak >nul")
    else:
        import time
        time.sleep(10)

if __name__ == "__main__":
    main()