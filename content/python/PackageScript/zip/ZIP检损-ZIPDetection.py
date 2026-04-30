"""
ZIP 文件完整性检查工具
功能：递归扫描指定目录下的所有 ZIP 文件，测试它们是否损坏，并输出损坏的文件列表
"""

import os
import sys
import zipfile
from tqdm import tqdm

# ===================== 用户配置区域 =====================
DEFAULT_TARGET_DIR = r"D:\0libZip"  # 需要扫描的目录
# ======================================================

def validate_environment(target_dir: str) -> tuple:
    """
    验证目标目录是否存在且有效
    返回：(是否有效, 错误信息)
    """
    if not os.path.exists(target_dir):
        return False, f"目标目录不存在: {target_dir}"
    if not os.path.isdir(target_dir):
        return False, f"路径不是目录: {target_dir}"
    return True, ""

def check_zip_integrity(zip_path: str) -> tuple:
    """
    检查单个 ZIP 文件的完整性
    参数：
        zip_path: ZIP 文件的完整路径
    返回：
        (是否完整, 错误描述)
        完整时错误描述为空字符串
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # testzip() 返回第一个损坏文件的名称，若无损坏返回 None
            damaged_file = zf.testzip()
            if damaged_file is not None:
                return False, f"文件内 {damaged_file} 损坏 (CRC 校验失败)"
            # 可选：进一步尝试读取所有文件信息（testzip 已足够）
            # 确保文件列表可读
            _ = zf.namelist()
        return True, ""
    except zipfile.BadZipFile:
        return False, "文件结构损坏或不是有效的 ZIP 文件"
    except FileNotFoundError:
        return False, "文件不存在"
    except PermissionError:
        return False, "权限不足，无法读取文件"
    except Exception as e:
        return False, f"未知错误: {str(e)}"

def main(target_dir: str):
    """主处理流程"""
    # 环境验证
    valid, err_msg = validate_environment(target_dir)
    if not valid:
        print(f"错误: {err_msg}")
        sys.exit(1)

    # 递归扫描所有 ZIP 文件
    zip_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(".zip"):
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):
                    zip_files.append(full_path)

    if not zip_files:
        print("未找到任何 ZIP 文件。")
        return

    # 存储损坏的文件信息
    damaged_files = []  # 每个元素为 (文件路径, 错误信息)

    # 初始化进度条并逐文件检查
    with tqdm(zip_files, desc="检查进度", unit="file", colour="green") as pbar:
        for zip_path in pbar:
            base_name = os.path.basename(zip_path)
            pbar.set_postfix(file=base_name[:30])  # 显示文件名前30字符

            is_ok, error_msg = check_zip_integrity(zip_path)

            if is_ok:
                pbar.write(f"[✓] 正常: {base_name}")
            else:
                damaged_files.append((zip_path, error_msg))
                pbar.write(f"[✗] 损坏: {base_name} - {error_msg}")

    # 输出汇总信息
    total = len(zip_files)
    damaged_count = len(damaged_files)
    print(f"\n检查完成！总计 {total} 个 ZIP 文件，其中 {damaged_count} 个损坏。")

    if damaged_files:
        print("\n===== 损坏文件列表 =====")
        for path, err in damaged_files:
            print(f"路径: {path}")
            print(f"原因: {err}\n")
    else:
        print("所有 ZIP 文件均完好无损。")

    # 仅在 Windows 下尝试打开目标文件夹（可选）
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
            print("若不指定目录，则使用脚本内 DEFAULT_TARGET_DIR 的值。")
            sys.exit(0)
        target_directory = sys.argv[1]

    main(target_directory)