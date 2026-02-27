import os

def get_size_kb(file_path):
    """获取文件大小，单位为 KB"""
    size = os.path.getsize(file_path)
    return size / 1024

def find_duplicates_and_move(src_path, dest_path):
    """查找大小相同的文件并移动到指定路径"""
    # 获取指定路径下的所有文件
    all_files = os.listdir(src_path)
    
    # 用于存储文件大小的字典
    file_sizes = {}
    
    for file_name in all_files:
        file_path = os.path.join(src_path, file_name)
        if os.path.isfile(file_path):
            file_size = get_size_kb(file_path)
            if file_size in file_sizes:
                file_sizes[file_size].append(file_path)
            else:
                file_sizes[file_size] = [file_path]
    
    # 移动符合要求的文件
    for file_size, file_paths in file_sizes.items():
        if len(file_paths) > 1:
            for file_path in file_paths:
                # 构建目标路径
                dest_file_path = os.path.join(dest_path, os.path.basename(file_path))
                # 移动文件
                os.rename(file_path, dest_file_path)
                print(f"Moved {file_path} to {dest_file_path}")

# 使用示例
find_duplicates_and_move(r"D:\newmusic2024.3.6", r"D:\new")
