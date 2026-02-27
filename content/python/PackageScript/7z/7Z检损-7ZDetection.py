"""
7z压缩包完整性检测工具
功能：检测指定目录下所有7z压缩包的完整性（仅支持无密码压缩包）
"""

import os
import subprocess

# ===================== 用户配置区域 =====================
SEVEN_7Z_PATH = r"C:\Program File\7-Zip\7z.exe"  # 7Z可执行文件路径
TARGET_DIRECTORY = r"C:\Users\chru\Desktop\UE-VRGK-v2-master"  # 需要检测的目录
# ======================================================

def validate_environment() -> tuple:
    """
    验证系统环境是否满足运行要求
    返回：(是否有效, 错误消息列表)
    """
    errors = []

    # 检查7z程序是否存在
    if not os.path.isfile(SEVEN_7Z_PATH):
        errors.append(f"7z程序不存在于 {SEVEN_7Z_PATH}")
    
    # 检查目标目录有效性
    if not os.path.exists(TARGET_DIRECTORY):
        errors.append(f"目标目录不存在: {TARGET_DIRECTORY}")
    elif not os.path.isdir(TARGET_DIRECTORY):
        errors.append(f"路径不是目录: {TARGET_DIRECTORY}")

    return (len(errors) == 0), errors

def scan_7z_files(directory: str) -> list:
    """
    扫描目录下所有7z文件
    参数：
        directory: 要扫描的目录路径
    返回：
        找到的7z文件路径列表
    """
    print(f"\n开始扫描目录: {directory}")
    sevenz_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            # 精确匹配.7z扩展名（不区分大小写）
            if os.path.splitext(file)[1].lower() == '.7z':
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):  # 过滤有效文件
                    sevenz_files.append(full_path)
    
    print(f"找到 {len(sevenz_files)} 个7z文件")
    return sevenz_files

def check_7z_integrity(file_list: list) -> list:
    """
    检查7z文件完整性
    参数：
        file_list: 要检查的文件路径列表
    返回：
        损坏文件路径列表
    """
    corrupted_files = []
    
    print("\n开始检测文件完整性...")
    for idx, file_path in enumerate(file_list, 1):
        print(f"正在检测 ({idx}/{len(file_list)}): {os.path.basename(file_path)}")
        
        try:
            # 使用7z测试命令检测压缩包完整性
            # 参数说明：
            # t : 测试压缩包完整性
            # -bse0 : 禁用错误信息输出
            subprocess.run(
                [SEVEN_7Z_PATH, 't', '-bse0', file_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True
            )
        except subprocess.CalledProcessError:
            # 返回码非零表示文件损坏
            corrupted_files.append(file_path)
            print(f"  → 损坏")
        except Exception as e:
            print(f"  → 检测失败: {str(e)}")
            corrupted_files.append(file_path)
    
    return corrupted_files

def print_results(corrupted_files: list):
    """格式化输出检测结果"""
    print("\n" + "="*50)
    print("检测结果汇总：")
    
    if corrupted_files:
        print(f"\033[31m发现 {len(corrupted_files)} 个损坏文件\033[0m")
        for path in corrupted_files:
            print(f"  • {path}")
    else:
        print("\033[32m所有7z文件均完整有效\033[0m")
    
    print("="*50)

def main():
    # 环境验证
    is_valid, errors = validate_environment()
    if not is_valid:
        print("\n".join(["\033[31m错误:\033[0m"] + errors))
        return
    
    # 扫描文件
    file_list = scan_7z_files(TARGET_DIRECTORY)
    if not file_list:
        print("未找到可检测的7z文件")
        return
    
    # 执行检测
    bad_files = check_7z_integrity(file_list)
    
    # 输出结果
    print_results(bad_files)

if __name__ == "__main__":
    main()