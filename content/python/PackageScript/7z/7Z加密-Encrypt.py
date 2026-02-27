"""
7z压缩包加密工具
功能：为指定目录下的7z压缩包添加密码保护并生成新文件
"""

import os
import sys
import subprocess
import tempfile
import platform
from tqdm import tqdm
from typing import Tuple

# ===================== 用户配置区域 =====================
DEFAULT_TARGET_DIR = r"C:\Users\chru\Desktop\UE-VRGK-v2-master"  # 默认处理目录
DEFAULT_PASSWORD = "123"                            # 默认压缩包密码
possible_paths = [r"C:\Program File\7-Zip\7z.exe"]  # 7Z可执行文件路径
# ======================================================

def validate_system_environment(target_dir: str) -> Tuple[bool, dict]:
    """
    验证系统环境是否满足运行要求
    参数：
        target_dir: 目标目录路径
    返回：
        tuple: (验证结果, 错误信息字典)
    """
    validation_errors = {
        "missing_tools": [],
        "dir_errors": []
    }

    # 检查7z可执行文件
    seven_zip_path = find_7z_executable()
    if not os.path.isfile(seven_zip_path) and seven_zip_path == "7z":
        validation_errors["missing_tools"].append("7-Zip (未找到可执行文件且不在系统PATH中)")

    # 检查目标目录
    if not os.path.exists(target_dir):
        validation_errors["dir_errors"].append(f"目标目录不存在: {target_dir}")
    elif not os.path.isdir(target_dir):
        validation_errors["dir_errors"].append(f"路径不是目录: {target_dir}")

    is_valid = len(validation_errors["missing_tools"]) == 0 and len(validation_errors["dir_errors"]) == 0
    return is_valid, validation_errors

def find_7z_executable() -> str:
    """
    查找系统上的7z可执行文件路径
    返回：
        str: 7z可执行文件路径
    """
    system = platform.system()
    if system == "Windows":
        for path in possible_paths:
            if os.path.isfile(path):
                return path
    return "7z"  # 非Windows系统或未找到时尝试PATH环境变量

def create_silent_process_config() -> Tuple[subprocess.STARTUPINFO, int]:
    """
    创建静默运行配置（适用于Windows系统）
    返回：
        tuple: (startupinfo, creationflags)
    """
    startupinfo = None
    creationflags = 0
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW
    return startupinfo, creationflags

def process_archive(original_path: str, new_path: str, password: str, seven_zip: str) -> Tuple[bool, str]:
    """
    处理单个压缩包加密流程
    参数：
        original_path: 原始文件路径
        new_path: 新文件路径
        password: 加密密码
        seven_zip: 7z可执行文件路径
    返回：
        tuple: (操作是否成功, 错误信息)
    """
    startupinfo, creationflags = create_silent_process_config()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 阶段1：解压原始压缩包
            # 参数说明：
            # x - 解压命令
            # -y - 确认所有操作
            # -o - 输出目录
            subprocess.run(
                [seven_zip, "x", original_path, f"-o{temp_dir}", "-y"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=creationflags
            )

            # 阶段2：创建加密压缩包
            # 参数说明：
            # a - 添加文件
            # -p - 设置密码
            # -mhe=on - 加密文件头
            subprocess.run(
                [seven_zip, "a", new_path, ".", f"-p{password}", "-mhe=on"],
                cwd=temp_dir,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            return True, ""
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode().strip() if e.stderr else str(e)
        # 清理可能创建的部分文件
        if os.path.exists(new_path):
            os.remove(new_path)
        return False, f"子进程错误: {error_msg}"
    except Exception as e:
        if os.path.exists(new_path):
            os.remove(new_path)
        return False, f"意外错误: {str(e)}"

def main(target_dir: str, password: str):
    """
    主处理流程
    参数：
        target_dir: 目标目录路径
        password: 压缩包密码
    """
    # 环境验证
    is_valid, validation = validate_system_environment(target_dir)
    if not is_valid:
        if validation["missing_tools"]:
            print("缺少必要程序：")
            for tool in validation["missing_tools"]:
                print(f"  - {tool}")
        if validation["dir_errors"]:
            print("目录错误：")
            for err in validation["dir_errors"]:
                print(f"  - {err}")
        sys.exit(1)

    # 获取7z可执行文件路径
    seven_zip = find_7z_executable()

    # 扫描目标目录
    archive_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(".7z"):
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):
                    archive_files.append(full_path)

    # 初始化进度条
    with tqdm(archive_files, desc="加密进度", unit="file", colour="yellow") as pbar:
        success_count = 0
        for src_path in pbar:
            base_name = os.path.basename(src_path)
            new_filename = f"{os.path.splitext(base_name)[0]}_encrypted.7z"
            dst_path = os.path.join(os.path.dirname(src_path), new_filename)
            pbar.set_postfix(file=base_name[:20])  # 显示文件名前20字符

            # 执行加密操作
            is_success, message = process_archive(src_path, dst_path, password, seven_zip)
            
            if is_success:
                success_count += 1
                pbar.write(f"[✓] 加密成功: {base_name}")
            else:
                pbar.write(f"[✕] 加密失败: {base_name} - {message}")

    # 输出统计信息
    print(f"\n处理完成！成功加密 {success_count}/{len(archive_files)} 个文件")
    
    # 打开目标文件夹（仅Windows）
    if os.name == 'nt':
        try:
            os.startfile(target_dir)
        except Exception as e:
            print(f"无法打开目录: {str(e)}")

if __name__ == "__main__":
    # 处理命令行参数
    target_directory = DEFAULT_TARGET_DIR
    archive_password = DEFAULT_PASSWORD

    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ("-h", "--help"):
            print("使用方法: python script.py [目标目录] [密码]")
            sys.exit(0)
        target_directory = sys.argv[1]
        
    if len(sys.argv) > 2:
        archive_password = sys.argv[2]

    main(target_directory, archive_password)