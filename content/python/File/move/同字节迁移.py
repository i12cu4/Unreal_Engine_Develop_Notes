import os
import shutil
import argparse

def get_unique_filename(dest_dir, filename):
    """生成目标目录中唯一的文件名，避免冲突"""
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    dest_path = os.path.join(dest_dir, new_filename)
    # 检查是否存在同名文件，若存在则递增编号
    while os.path.exists(dest_path):
        new_filename = f"{base}_{counter}{ext}"
        dest_path = os.path.join(dest_dir, new_filename)
        counter += 1
    return new_filename

def find_duplicate_sizes(source_dir):
    """遍历源目录，统计文件大小并返回重复大小的文件列表"""
    size_counts = {}
    file_list = []
    # 遍历所有文件并记录大小
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_list.append((file_path, file_size))
                size_counts[file_size] = size_counts.get(file_size, 0) + 1
    # 筛选出大小重复的文件
    duplicates = [fp for fp, fs in file_list if size_counts[fs] >= 2]
    return duplicates

def move_files(files_to_move, dest_dir):
    """将文件移动到目标目录，处理文件名冲突"""
    os.makedirs(dest_dir, exist_ok=True)
    for file_path in files_to_move:
        filename = os.path.basename(file_path)
        unique_name = get_unique_filename(dest_dir, filename)
        dest_path = os.path.join(dest_dir, unique_name)
        # 移动文件
        shutil.move(file_path, dest_path)
        print(f"Moved '{file_path}' to '{dest_path}'")

def main(source_dir, dest_dir):
    # 查找所有需要移动的文件
    duplicates = find_duplicate_sizes(source_dir)
    # 移动文件到目标目录
    move_files(duplicates, dest_dir)
    print(f"Total files moved: {len(duplicates)}")

if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser(description='移动重复大小的文件到指定目录')
    parser.add_argument('source_dir', help='源目录路径')
    parser.add_argument('dest_dir', help='目标目录路径')
    args = parser.parse_args()
    main(args.source_dir, args.dest_dir)
    """

    source_dir = r"F:"
    dest_dir = r"F:\com"
    main(source_dir, dest_dir)