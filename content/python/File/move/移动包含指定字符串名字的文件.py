# 移动包含指定字符串名字的文件
import os
import shutil


def move_files_with_string(source_dir, target_dir, search_string):
    # 检查源文件夹是否存在
    if not os.path.exists(source_dir):
        print(f"源文件夹不存在: {source_dir}")
        return

    # 如果目标文件夹不存在，则创建它
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"创建目标文件夹: {target_dir}")

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)

        # 检查是否是文件（跳过文件夹）
        if os.path.isfile(file_path) and search_string in filename:
            # 构造目标文件路径
            target_file_path = os.path.join(target_dir, filename)

            try:
                # 移动文件
                shutil.move(file_path, target_file_path)
                print(f"移动文件: {filename} -> {target_dir}")
            except Exception as e:
                # 捕获并提示移动失败的原因
                print(f"移动文件失败: {filename} ({e})")


# 示例用法
source_directory = r"D:\newmusic"  # 源文件夹路径
target_directory = r"D:\temp"  # 目标文件夹路径
search_string = "？"  # 文件名中需要包含的字符串

move_files_with_string(source_directory, target_directory, search_string)
