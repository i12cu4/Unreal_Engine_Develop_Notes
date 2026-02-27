"""
RAR文件检验损坏脚本
功能：对指定目录下的所有RAR文件进行检验损坏，并输出损坏的文件列表
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional

# ===================== 用户配置区域 =====================
TARGET_DIRECTORY = r"C:\Users\chru\Downloads\agw"  # 目标目录
WINRAR_PATHS = [                                             # WinRAR可能路径
    r"C:\Program File\WinRAR\WinRar.exe"  # 容错可能的拼写错误
]
# ======================================================

def get_winrar_path() -> str:
    """获取有效的WinRAR可执行文件路径"""
    # 检查用户配置路径
    for path in WINRAR_PATHS:
        if os.path.isfile(path):
            return path
    
    for path in WINRAR_PATHS:
        if os.path.isfile(path):
            return path
    
    raise FileNotFoundError("无法找到WinRAR可执行文件，请检查安装或配置路径")

def test_rar_file(winrar_path: str, rar_path: Path) -> bool:
    """测试单个RAR文件是否损坏"""
    try:
        result = subprocess.run(
            [winrar_path, 't', str(rar_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
            check=False
        )
        return result.returncode != 0
    except Exception as e:
        print(f"测试文件 {rar_path} 时发生异常：{str(e)}")
        return True  # 将异常情况视为损坏

def find_damaged_rar_files(winrar_path: str, target_dir: Path) -> List[str]:
    """查找损坏的RAR文件"""
    damaged_files = []
    
    # 遍历所有RAR文件（包括子目录）
    for rar_file in target_dir.rglob('*.rar'):
        print(f"正在检测文件：{rar_file}...", end='', flush=True)
        
        if test_rar_file(winrar_path, rar_file):
            print(" [损坏]")
            damaged_files.append(str(rar_file))
        else:
            print(" [正常]")
    
    return damaged_files

def main():
    try:
        # 获取WinRAR路径
        winrar_path = get_winrar_path()
        print(f"使用的WinRAR路径：{winrar_path}")
        
        # 验证目标目录
        target_dir = Path(TARGET_DIRECTORY)
        if not target_dir.is_dir():
            raise ValueError(f"目标路径 {TARGET_DIRECTORY} 不是有效目录")
        
        # 执行检测
        damaged_files = find_damaged_rar_files(winrar_path, target_dir)
        
        # 输出结果
        print("\n检测完成，损坏文件列表：")
        if damaged_files:
            for idx, file in enumerate(damaged_files, 1):
                print(f"{idx}. {file}")
        else:
            print("未发现损坏的RAR文件")
            
    except Exception as e:
        print(f"程序运行出错：{str(e)}")

if __name__ == "__main__":
    main()