import os
import re
import send2trash
from pathlib import Path

def find_duplicate_files(directory_path):
    """
    在指定目录中查找重复文件
    
    Args:
        directory_path (str): 要扫描的目录路径
        
    Returns:
        dict: 包含重复文件信息的字典
    """
    # 存储文件分组信息
    file_groups = {}
    
    # 遍历目录中的所有文件
    for file_path in Path(directory_path).rglob('*'):
        if file_path.is_file():
            filename = file_path.name
            file_size = file_path.stat().st_size
            
            # 使用正则表达式匹配文件名模式
            # 匹配 xxx(1).ext 或 xxx - 副本.ext 等模式
            pattern = r'^(.*?)(?:\s*[\(\-\s]*(?:副本|copy|\d+)[\)\-\s]*)(\..+)?$'
            match = re.match(pattern, filename, re.IGNORECASE)
            
            if match:
                # 提取基础文件名和扩展名
                base_name = match.group(1).strip()
                extension = match.group(2) if match.group(2) else file_path.suffix
                
                # 构建原始文件名
                original_filename = base_name + extension
                original_file_path = file_path.parent / original_filename
                
                # 检查原始文件是否存在且大小相同
                if original_file_path.exists():
                    original_file_size = original_file_path.stat().st_size
                    
                    if original_file_size == file_size:
                        group_key = (original_file_path, original_file_size)
                        if group_key not in file_groups:
                            file_groups[group_key] = []
                        file_groups[group_key].append(file_path)
    
    return file_groups

def move_duplicates_to_trash(duplicate_groups):
    """
    将重复文件移动到回收站
    
    Args:
        duplicate_groups (dict): 重复文件分组信息
    """
    moved_files = []
    
    for (original_file, original_size), duplicates in duplicate_groups.items():
        print(f"\n原始文件: {original_file.name}")
        print(f"大小: {original_size} 字节")
        print("重复文件:")
        
        for duplicate in duplicates:
            print(f"  - {duplicate}")
            try:
                # 移动到回收站
                send2trash.send2trash(str(duplicate))
                moved_files.append(duplicate)
                print(f"    ✓ 已移动到回收站")
            except Exception as e:
                print(f"    ✗ 移动失败: {e}")
    
    return moved_files

def main():
    """
    主函数：执行重复文件清理
    """
    # 设置要扫描的目录路径
    directory_path = input("请输入要扫描的目录路径: ").strip()
    
    if not directory_path:
        directory_path = "."  # 默认当前目录
    
    if not os.path.exists(directory_path):
        print(f"错误: 路径 '{directory_path}' 不存在")
        return
    
    print(f"开始扫描目录: {directory_path}")
    print("正在查找重复文件...")
    
    # 查找重复文件
    duplicate_groups = find_duplicate_files(directory_path)
    
    if not duplicate_groups:
        print("\n未找到重复文件")
        return
    
    total_duplicates = sum(len(duplicates) for duplicates in duplicate_groups.values())
    print(f"\n找到 {len(duplicate_groups)} 组重复文件，共 {total_duplicates} 个重复文件")
    
    # 显示找到的重复文件
    print("\n重复文件列表:")
    for i, ((original_file, original_size), duplicates) in enumerate(duplicate_groups.items(), 1):
        print(f"\n{i}. 原始文件: {original_file.name}")
        print(f"   路径: {original_file}")
        print(f"   大小: {original_size} 字节")
        print(f"   重复文件:")
        for duplicate in duplicates:
            print(f"     - {duplicate}")
    
    # 确认是否删除
    confirm = input(f"\n确定要将这 {total_duplicates} 个重复文件移动到回收站吗？(y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        print("\n开始移动重复文件到回收站...")
        moved_files = move_duplicates_to_trash(duplicate_groups)
        print(f"\n完成! 已移动 {len(moved_files)} 个文件到回收站")
    else:
        print("操作已取消")

def safe_test():
    """
    安全测试函数：只显示会删除的文件，不实际删除
    """
    test_directory = input("请输入要测试的目录路径: ").strip()
    
    if not test_directory:
        test_directory = "."
    
    if not os.path.exists(test_directory):
        print(f"错误: 路径 '{test_directory}' 不存在")
        return
    
    print(f"安全测试模式 - 只显示结果，不实际删除")
    print(f"扫描目录: {test_directory}")
    
    duplicate_groups = find_duplicate_files(test_directory)
    
    if not duplicate_groups:
        print("\n未找到重复文件")
        return
    
    total_duplicates = sum(len(duplicates) for duplicates in duplicate_groups.values())
    print(f"\n找到 {len(duplicate_groups)} 组重复文件，共 {total_duplicates} 个重复文件")
    
    print("\n以下文件会被移动到回收站:")
    for i, ((original_file, original_size), duplicates) in enumerate(duplicate_groups.items(), 1):
        print(f"\n{i}. 保留: {original_file}")
        print(f"   删除:")
        for duplicate in duplicates:
            print(f"     - {duplicate}")

if __name__ == "__main__":
    print("重复文件清理工具")
    print("1. 完整模式 (查找并删除重复文件)")
    print("2. 安全测试模式 (只显示结果，不删除)")
    
    choice = input("请选择模式 (1/2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        safe_test()
    else:
        print("无效选择")