# 移动表格中出现文件的路径
import os
import shutil

# 定义文件路径和目标路径

markdown_filepath = r"D:\Download\MovepackList\迁移compare\不同大小的文件1.md"
path_a = r"E:\agw"  # 替换为实际的搜索路径
path_b = r"D:\compare4"  # 替换为实际的目标路径

# 读取Markdown文件并解析文件名
filenames = []
with open(markdown_filepath, "r", encoding="utf-8") as file:
    lines = file.readlines()
    for line in lines:
        # 假设文件名在第一列，并且以竖线分隔
        parts = line.strip().split("|")
        if len(parts) > 1:
            filename = parts[1].strip()
            if filename:  # 确保文件名不为空
                filenames.append(filename)

# 遍历路径A，移动找到的文件
for root, dirs, files in os.walk(path_a):
    for filename in files:
        if filename in filenames:
            # 构建完整的源文件路径和目标文件路径
            src_file_path = os.path.join(root, filename)
            dst_file_path = os.path.join(path_b, filename)
            # 检查目标路径中是否已存在同名文件
            if os.path.exists(dst_file_path):
                print(
                    f"File '{filename}' already exists at '{path_b}'. Skipping to avoid overwrite."
                )
                continue
            # 移动文件
            shutil.move(src_file_path, dst_file_path)
            print(f"Moved '{filename}' to '{path_b}'")

print("Done")
