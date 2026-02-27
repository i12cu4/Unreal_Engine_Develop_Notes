# 文件重命名替换特定字符
import os


def rename_files_in_directory(directory, old_str, new_str):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if old_str in filename:
                new_filename = filename.replace(old_str, new_str)
                old_file_path = os.path.join(root, filename)
                new_file_path = os.path.join(root, new_filename)

                try:
                    # 尝试重命名文件
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed: {filename} -> {new_filename}")
                except FileExistsError:
                    # 如果目标文件名已存在，跳过并提示
                    print(
                        f"Skipped: {filename} -> {new_filename} (File already exists)"
                    )
                except Exception as e:
                    # 捕获其他可能的异常
                    print(f"Error renaming {filename}: {e}")


# 示例用法
directory_path = r"D:\newmusic"  # 替换为你的文件夹路径
# directory_path = r'D:\temp'  # 替换为你的文件夹路径
old_string = "스카이리(SKYLE)"  # 要替换的字符串
new_string = "SKYLE"  # 替换后的字符串

rename_files_in_directory(directory_path, old_string, new_string)
