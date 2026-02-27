"""
ZIP文件批量加密工具
功能：使用AES-256加密重新打包指定目录下的所有ZIP文件
支持加密压缩包的解压和重新加密
"""

import os
import tempfile
import shutil
import pyzipper
from tqdm import tqdm
import argparse

# ===================== 用户配置区域 =====================
TARGET_DIRECTORY = r"C:\Users\chru\Desktop\UE-VRGK-v2-master"  # 目标目录
DEFAULT_PASSWORD = "1234" # 默认加密密码（建议修改为强密码）
# ======================================================

def validate_system_environment():
    """
    验证系统环境是否满足运行要求
    返回验证结果和错误消息
    """
    # 检查第三方库安装
    try:
        pyzipper.AESZipFile
    except AttributeError:
        print("错误：未安装pyzipper库（请运行pip install pyzipper）")
        return False, "依赖库缺失"

    # 检查目标目录有效性
    if not os.path.isdir(TARGET_DIRECTORY):
        print(f"错误：目标目录不存在 - {TARGET_DIRECTORY}")
        return False, "目录无效"

    return True, None

def encrypt_zip_file(zip_path, password, temp_dir):
    """
    单个ZIP文件加密处理流程
    参数：
        zip_path - 原始ZIP文件路径
        password - 加密密码
        temp_dir - 临时工作目录
    返回：加密后的新文件路径
    """
    # 创建临时解压目录
    extract_path = os.path.join(temp_dir, os.path.basename(zip_path))
    os.makedirs(extract_path, exist_ok=True)

    try:
        # 1. 解压原始文件
        with pyzipper.AESZipFile(zip_path) as zin:
            zin.pwd = password.encode()
            zin.extractall(extract_path)

        # 2. 创建加密压缩包
        new_name = os.path.splitext(zip_path)[0] + "_encrypted.zip"
        new_path = os.path.join(os.path.dirname(zip_path), new_name)

        with pyzipper.AESZipFile(new_path, 'w', 
                                compression=pyzipper.ZIP_DEFLATED,
                                encryption=pyzipper.WZ_AES) as zout:
            zout.setpassword(password.encode())
            
            # 递归添加文件
            for root, _, files in os.walk(extract_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extract_path)
                    zout.write(file_path, arcname)

        # 3. 文件完整性验证
        with pyzipper.AESZipFile(new_path) as check_file:
            check_file.pwd = password.encode()
            check_file.testzip()  # 触发完整性校验

        return new_path

    except Exception as e:
        print(f"处理文件 {zip_path} 时出错: {str(e)}")
        return None
    finally:
        # 清理临时文件
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)

def encrypt_existing_zips(target_dir, password):
    """
    批量处理流程
    参数：
        target_dir - 目标目录路径
        password - 加密密码
    """
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="zip_encrypt_")
    
    try:
        # 1. 扫描ZIP文件
        zip_files = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.lower().endswith(".zip"):
                    zip_files.append(os.path.join(root, file))

        if not zip_files:
            print("未发现任何ZIP文件")
            return 1

        print(f"发现{len(zip_files)}个ZIP文件，开始处理...")

        # 2. 批量处理
        success_count = 0
        with tqdm(total=len(zip_files)) as pbar:
            for zip_path in zip_files:
                new_path = encrypt_zip_file(zip_path, password, temp_dir)
                if new_path:
                    success_count += 1
                    print(f"成功创建加密文件: {new_path}")
                    print(f"验证命令: 7z x '{new_path}' -ppassword")
                pbar.update(1)

        print(f"处理完成：成功{success_count}/{len(zip_files)}")

    except Exception as e:
        print(f"批量处理异常: {str(e)}")
        return 1
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description='ZIP文件批量加密工具')
    parser.add_argument('-d', '--directory', 
                      default=TARGET_DIRECTORY,
                      help='目标目录（默认: 当前配置目录）')
    parser.add_argument('-p', '--password', 
                      default=DEFAULT_PASSWORD,
                      help='加密密码（默认: 123）')
    parser.add_argument('-v', '--verbose', 
                      action='store_true',
                      help='启用详细输出模式')
    args = parser.parse_args()

    # 1. 环境验证
    is_valid, error_msg = validate_system_environment()
    if not is_valid:
        print(f"环境验证失败: {error_msg}")
        exit(1)

    # 2. 执行加密
    exit_code = encrypt_existing_zips(args.directory, args.password)
    
    # 3. 程序退出
    print(f"程序退出码：{exit_code}")
    exit(exit_code)
