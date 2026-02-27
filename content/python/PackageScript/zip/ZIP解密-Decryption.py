"""
ZIP文件密码移除工具
功能：移除指定目录下ZIP文件的密码保护并生成新文件
注意：需要安装pyzipper库（pip install pyzipper）
"""

import os
import tempfile
import pyzipper
from tqdm import tqdm

# ===================== 用户配置区域 =====================
TARGET_DIRECTORY = r"C:\Users\chru\Desktop\UE-VRGK-v2-master"  # 需要处理的目录
PASSWORD = "1234"                                      # 原始压缩包密码
OUTPUT_SUFFIX = "_nopassword"                         # 新文件后缀
COMPRESSION_METHOD = pyzipper.ZIP_DEFLATED            # 压缩方式
# ======================================================

def validate_environment() -> tuple:
    """
    验证系统环境是否满足运行要求
    返回：(是否有效, 错误消息列表)
    """
    errors = []

    # 检查目标目录有效性
    if not os.path.exists(TARGET_DIRECTORY):
        errors.append(f"目标目录不存在: {TARGET_DIRECTORY}")
    elif not os.path.isdir(TARGET_DIRECTORY):
        errors.append(f"路径不是目录: {TARGET_DIRECTORY}")

    return (len(errors) == 0), errors

def scan_zip_files(directory: str) -> list:
    """
    扫描目录下所有ZIP文件
    参数：
        directory: 要扫描的目录路径
    返回：
        找到的ZIP文件路径列表（绝对路径）
    """
    print(f"\n开始扫描目录: {directory}")
    zip_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.zip'):
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):  # 过滤有效文件
                    zip_files.append(full_path)
    
    print(f"找到 {len(zip_files)} 个ZIP文件")
    return zip_files

def process_zip_file(input_path: str) -> tuple:
    """
    处理单个ZIP文件去密码
    参数：
        input_path: 原始文件路径
    返回：
        (是否成功, 新文件路径, 错误信息)
    """
    try:
        # 生成输出路径
        dir_name = os.path.dirname(input_path)
        base_name = os.path.basename(input_path)
        new_name = f"{os.path.splitext(base_name)[0]}{OUTPUT_SUFFIX}.zip"
        new_path = os.path.join(dir_name, new_name)

        with tempfile.TemporaryDirectory() as temp_dir:
            # 阶段1：解压原始文件
            try:
                with pyzipper.AESZipFile(input_path) as orig_zip:
                    orig_zip.extractall(temp_dir, pwd=PASSWORD.encode('utf-8'))
            except RuntimeError as e:
                if "Bad password" in str(e):
                    return False, input_path, "密码错误"
                raise
            except pyzipper.BadZipFile:
                return False, input_path, "损坏的ZIP文件"

            # 阶段2：创建无密码压缩包
            with pyzipper.ZipFile(
                new_path,
                'w',
                compression=COMPRESSION_METHOD
            ) as new_zip:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        new_zip.write(file_path, arcname)

            # 验证新文件
            try:
                with pyzipper.ZipFile(new_path) as test_zip:
                    test_zip.testzip()
            except Exception:
                os.remove(new_path)
                return False, input_path, "新文件验证失败"

            return True, new_path, ""

    except PermissionError:
        return False, input_path, "文件访问被拒绝"
    except Exception as e:
        return False, input_path, f"未知错误: {str(e)}"

def print_summary(results: list):
    """打印处理结果摘要"""
    print("\n" + "="*50)
    print("处理结果汇总：")
    
    success = sum(1 for r in results if r[0])
    failures = len(results) - success

    print(f"\033[32m成功: {success} 个文件\033[0m")
    print(f"\033[31m失败: {failures} 个文件\033[0m")
    
    if failures > 0:
        print("\n失败详情：")
        for success, path, reason in (r for r in results if not r[0]):
            print(f"• {os.path.basename(path)}: {reason}")

    print("="*50)
    print("提示：原始文件未被修改")

def main():
    # 环境验证
    is_valid, errors = validate_environment()
    if not is_valid:
        print("\n".join(["\033[31m错误:\033[0m"] + errors))
        return

    # 扫描文件
    zip_files = scan_zip_files(TARGET_DIRECTORY)
    if not zip_files:
        print("未找到需要处理的ZIP文件")
        return

    # 处理文件
    results = []
    with tqdm(zip_files, desc="处理进度", unit="file", colour="green") as pbar:
        for file_path in pbar:
            pbar.set_postfix(file=os.path.basename(file_path)[:20])
            
            success, new_path, message = process_zip_file(file_path)
            results.append( (success, new_path, message) )
            
            if success:
                pbar.write(f"\033[32m✓ 成功创建: {os.path.basename(new_path)}\033[0m")
            else:
                pbar.write(f"\033[31m✕ 处理失败: {os.path.basename(file_path)} - {message}\033[0m")

    # 输出摘要
    print_summary(results)

if __name__ == "__main__":
    main()