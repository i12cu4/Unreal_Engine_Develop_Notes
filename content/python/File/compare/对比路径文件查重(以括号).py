# 对比路径文件查重(以括号),迁移目标文件
import os
import shutil


def move_files_with_brackets(source_dir, target_dir):
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
        if os.path.isfile(file_path):
            # 检查文件名是否包含括号
            if "(" in filename and ")" in filename:
                # 去掉括号及其内容
                new_filename = (
                    filename.split("(")[0].strip() + os.path.splitext(filename)[1]
                )

                # 检查去掉括号后的文件是否存在
                new_file_path = os.path.join(source_dir, new_filename)
                if os.path.exists(new_file_path):
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

move_files_with_brackets(source_directory, target_directory)
