import os
import shutil
from pathlib import Path

def rename_files_with_pattern(root_path, old_string, new_string):
    """
    重命名指定路径中文件名包含特定字符串的所有文件
    
    参数:
        root_path: 要搜索的根目录路径
        old_string: 要查找的字符串
        new_string: 要替换的新字符串
    """
    # 使用pathlib处理路径
    root_dir = Path(root_path)
    
    # 检查路径是否存在
    if not root_dir.exists():
        print(f"错误: 路径 '{root_path}' 不存在")
        return
    
    # 计数器
    renamed_count = 0
    
    print(f"开始扫描路径: {root_path}")
    print(f"查找包含 '{old_string}' 的文件名，替换为 '{new_string}'")
    print("-" * 50)
    
    # 遍历所有文件和子目录
    for file_path in root_dir.rglob('*'):
        # 只处理文件，跳过目录
        if file_path.is_file():
            # 获取文件名（不含路径）
            filename = file_path.name
            
            # 检查文件名是否包含目标字符串
            if old_string in filename:
                # 创建新文件名
                new_filename = filename.replace(old_string, new_string)
                
                # 如果文件名有变化
                if new_filename != filename:
                    # 构建新文件的完整路径
                    new_file_path = file_path.parent / new_filename
                    
                    try:
                        # 如果目标文件已存在，处理冲突
                        if new_file_path.exists():
                            new_file_path = handle_naming_conflict(new_file_path)
                            print(f"冲突! 重命名为: {new_file_path.name}")
                        
                        # 执行重命名
                        file_path.rename(new_file_path)
                        print(f"重命名: {filename} -> {new_file_path.name}")
                        renamed_count += 1
                        
                    except Exception as e:
                        print(f"重命名失败 {filename}: {e}")
    
    print("-" * 50)
    print(f"操作完成! 共重命名 {renamed_count} 个文件")

def handle_naming_conflict(file_path):
    """
    处理文件名冲突，生成新的唯一文件名
    
    参数:
        file_path: 冲突的文件路径
        
    返回:
        新的文件路径
    """
    parent = file_path.parent
    stem = file_path.stem
    suffix = file_path.suffix
    
    counter = 1
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def main():
    # 设置变量
    target_path = r"C:\Users\Administrator\Desktop\新建文件夹-251107-105946993\中华书局出版社精选500册"  # 请修改为你的实际路径
    string_to_find = "（精）"    # 要查找的字符串
    string_to_replace = "" # 要替换的字符串
    
    # 显示操作信息
    print("文件重命名程序")
    print(f"目标路径: {target_path}")
    print(f"查找字符串: '{string_to_find}'")
    print(f"替换为: '{string_to_replace}'")
    print()
    
    # 确认操作
    confirm = input("确认执行此操作？(y/n): ").lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 执行重命名
    rename_files_with_pattern(target_path, string_to_find, string_to_replace)

if __name__ == "__main__":
    main()