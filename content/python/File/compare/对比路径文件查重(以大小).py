# 对比路径文件查重(以大小),迁移目标文件
import os
from collections import defaultdict
import shutil


def move_files_with_same_size(src_path, dest_path):
    # 存储相同大小的文件列表
    size_dict = defaultdict(list)

    # 遍历源路径下的所有文件
    for root, dirs, files in os.walk(src_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            size_dict[file_size].append(file_path)

    # 检查目标路径是否存在，如果不存在则创建
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    # 移动相同大小的文件
    for size, files in size_dict.items():
        if len(files) > 1:  # 只处理有多个文件的相同大小
            for file in files:
                # 构建目标文件路径
                dest_file_path = os.path.join(dest_path, os.path.basename(file))
                # 移动文件
                shutil.move(file, dest_file_path)
                print(f"Moved: {file} -> {dest_file_path}")


# 指定源路径和目标路径
source_directory = r"D:\newmusic"
destination_directory = r"D:\temp"

# 调用函数
move_files_with_same_size(source_directory, destination_directory)
