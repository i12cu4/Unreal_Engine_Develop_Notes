"""
ZIP转RAR批量转换工具
功能：将指定目录及其子目录下所有ZIP文件转换为RAR格式
"""

import os
import subprocess
import tempfile
import shutil
import sys
from tqdm import tqdm

# ===================== 用户配置区域 =====================
DEFAULT_TARGET_DIR = r"C:\Users\chru\Downloads\comp"  # 需要扫描的zip文件目录
WINRAR_PATH = r"C:\Program File\WinRAR\WinRAR.exe"  # WinRAR可执行文件路径
# ======================================================

def validate_system_environment(target_dir: str) -> tuple:
    """
    验证系统环境是否满足运行要求
    参数：
        target_dir: 需要扫描的目标目录
    返回：
        tuple: (验证结果, 错误信息字典)
    """
    validation_errors = {
        "missing_tools": [],
        "dir_errors": []
    }

    # 检查WinRAR可执行文件是否存在
    if not os.path.isfile(WINRAR_PATH):
        validation_errors["missing_tools"].append(f"WinRAR ({WINRAR_PATH})")

    # 检查目标目录有效性
    if not os.path.exists(target_dir):
        validation_errors["dir_errors"].append(f"目标目录不存在: {target_dir}")
    elif not os.path.isdir(target_dir):
        validation_errors["dir_errors"].append(f"路径不是目录: {target_dir}")

    is_valid = len(validation_errors["missing_tools"]) == 0 and len(validation_errors["dir_errors"]) == 0
    return is_valid, validation_errors

def create_silent_process_config() -> tuple:
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

def convert_zip_to_rar(zip_file: str, rar_file: str) -> tuple:
    """
    执行ZIP转RAR转换操作
    参数：
        zip_file: 源ZIP文件完整路径
        rar_file: 目标RAR文件完整路径
    返回：
        tuple: (转换是否成功, 错误信息)
    """
    startupinfo, creationflags = create_silent_process_config()
    temp_dir = tempfile.mkdtemp()

    try:
        # 阶段1：解压ZIP文件到临时目录
        # 参数说明：
        # x - 解压命令
        # -ibck - 后台运行
        # -idq - 安静模式
        # -o+ - 覆盖已存在文件
        subprocess.run(
            [WINRAR_PATH, "x", "-ibck", "-idq", "-o+", zip_file, f"{temp_dir}\\"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=creationflags
        )

        # 阶段2：压缩为RAR文件
        # 参数说明：
        # a - 添加文件到压缩包
        # -idq - 安静模式
        # -ibck - 后台运行
        # -ep1 - 排除基本目录
        # -r - 递归子目录
        # -o+ - 覆盖已存在文件
        subprocess.run(
            [WINRAR_PATH, "a", "-idq", "-ibck", "-ep1", "-r", "-o+", rar_file, f"{temp_dir}\\*.*"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=creationflags
        )

        return True, ""
    except subprocess.CalledProcessError as e:
        return False, f"子进程执行错误: {e.returncode}"
    except Exception as e:
        return False, f"意外错误: {str(e)}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main(target_dir: str):
    """
    主处理流程
    参数：
        target_dir: 目标目录路径
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

    # 扫描目标目录
    zip_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(".zip"):
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):
                    zip_files.append(full_path)

    # 初始化进度条
    with tqdm(zip_files, desc="转换进度", unit="file", colour="blue") as pbar:
        success_count = 0
        for src_path in pbar:
            # 准备目标路径
            base_name = os.path.basename(src_path)
            dst_path = os.path.splitext(src_path)[0] + ".rar"
            pbar.set_postfix(file=base_name[:20])  # 显示前20个字符

            # 执行转换
            is_success, message = convert_zip_to_rar(src_path, dst_path)
            
            # 处理结果
            if is_success:
                success_count += 1
                pbar.write(f"[✓] 转换成功: {base_name}")
            else:
                pbar.write(f"[✕] 转换失败: {base_name} - {message}")

    # 输出统计信息
    print(f"\n转换完成！成功 {success_count}/{len(zip_files)} 个文件")
    
    # 打开目标文件夹（仅Windows）
    if os.name == 'nt':
        try:
            os.startfile(target_dir)
        except Exception as e:
            print(f"无法打开目录: {str(e)}")

if __name__ == "__main__":
    # 处理命令行参数
    target_directory = DEFAULT_TARGET_DIR
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ("-h", "--help"):
            print("使用方法: python script.py [目标目录]")
            sys.exit(0)
        target_directory = sys.argv[1]

    main(target_directory)