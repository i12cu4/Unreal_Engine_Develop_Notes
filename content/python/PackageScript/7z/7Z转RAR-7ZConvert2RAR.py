"""
7z转RAR批量转换工具
功能：将指定目录及其子目录下所有7z文件转换为RAR格式
"""

import os
import subprocess
import tempfile
import shutil
from tqdm import tqdm

# ===================== 用户配置区域 =====================
TARGET_DIRECTORY = r"C:\Users\chru\Desktop\UE-VRGK-v2-master"  # 需要扫描的7z文件目录
SEVEN_ZIP_PATH = r"C:\Program File\7-Zip\7z.exe"  # 7-Zip可执行文件路径
RAR_PATH = r"C:\Program File\WinRAR\WinRAR.exe"   # WinRAR可执行文件路径
# ======================================================

def validate_system_environment():
    """
    验证系统环境是否满足运行要求
    返回验证结果和错误消息
    """
    # 检查程序路径有效性
    missing_tools = []
    if not os.path.isfile(SEVEN_ZIP_PATH):
        missing_tools.append(f"7-Zip ({SEVEN_ZIP_PATH})")
    if not os.path.isfile(RAR_PATH):
        missing_tools.append(f"WinRAR ({RAR_PATH})")
    
    # 检查目标目录有效性
    dir_errors = []
    if not os.path.exists(TARGET_DIRECTORY):
        dir_errors.append(f"目标目录不存在: {TARGET_DIRECTORY}")
    elif not os.path.isdir(TARGET_DIRECTORY):
        dir_errors.append(f"路径不是目录: {TARGET_DIRECTORY}")
    
    return (len(missing_tools) == 0 and len(dir_errors) == 0), {
        "missing_tools": missing_tools,
        "dir_errors": dir_errors
    }

def create_silent_process_config():
    """创建静默运行配置（适用于Windows系统）"""
    startupinfo = None
    creationflags = 0
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW
    return startupinfo, creationflags

def convert_7z_to_rar(seven_zip_file: str, rar_file: str) -> bool:
    """
    执行7z转RAR转换操作
    参数：
        seven_zip_file: 源7z文件完整路径
        rar_file: 目标RAR文件完整路径
    返回：
        bool: 转换是否成功
        str: 错误信息（失败时）
    """
    startupinfo, creationflags = create_silent_process_config()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 阶段1：解压7z文件到临时目录
            # 参数说明：
            # x - 解压命令
            # -o{dir} - 指定输出目录
            # -y - 确认所有操作
            # -spd - 禁用进度显示
            subprocess.run(
                [SEVEN_ZIP_PATH, "x", f"-o{temp_dir}", seven_zip_file, "-y", "-spd"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags
            )

            # 阶段2：压缩为RAR文件
            # 参数说明：
            # a - 添加文件到压缩包
            # -idq - 安静模式运行
            # -ibck - 后台运行
            # -r - 递归子目录
            # -o+ - 覆盖已存在文件
            # -ep1 - 排除基本目录
            subprocess.run(
                [RAR_PATH, "a", "-idq", "-ibck", "-r", "-o+", "-ep1", rar_file, os.path.join(temp_dir, "*")],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            return True, ""
    except subprocess.CalledProcessError as e:
        return False, f"子进程执行错误: {str(e)}"
    except Exception as e:
        return False, f"意外错误: {str(e)}"

def main():
    """主处理流程"""
    # 环境验证
    is_valid, validation = validate_system_environment()
    if not is_valid:
        # 输出错误信息
        if validation["missing_tools"]:
            print("缺少必要程序：")
            for tool in validation["missing_tools"]:
                print(f"  - {tool}")
        if validation["dir_errors"]:
            print("目录错误：")
            for err in validation["dir_errors"]:
                print(f"  - {err}")
        exit(1)

    # 扫描目标目录
    sevenz_files = []
    for root, _, files in os.walk(TARGET_DIRECTORY):
        for file in files:
            if file.lower().endswith(".7z"):
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):  # 过滤无效条目
                    sevenz_files.append(full_path)

    # 初始化进度条
    with tqdm(sevenz_files, desc="转换进度", unit="file", colour="green") as pbar:
        success_count = 0
        for src_path in pbar:
            # 准备目标路径
            base_name = os.path.basename(src_path)
            dst_path = os.path.splitext(src_path)[0] + ".rar"
            pbar.set_postfix(file=base_name[:20])  # 显示前20个字符

            # 执行转换
            is_success, message = convert_7z_to_rar(src_path, dst_path)
            
            # 处理结果
            if is_success:
                success_count += 1
                pbar.write(f"[✓] 转换成功: {base_name}")
            else:
                pbar.write(f"[✕] 转换失败: {base_name} - {message}")

    # 输出统计信息
    print(f"\n转换完成！成功 {success_count}/{len(sevenz_files)} 个文件")
    
    # 打开目标文件夹（仅Windows）
    if os.name == 'nt':
        try:
            os.startfile(TARGET_DIRECTORY)
        except Exception as e:
            print(f"无法打开目录: {str(e)}")

if __name__ == "__main__":
    main()