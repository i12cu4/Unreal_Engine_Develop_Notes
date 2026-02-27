import os
import shutil

# 设置源目录和目标目录的路径
source_directory = r"D:\tempmuc"
target_directory = r"C:\Users\chru\Desktop\del"

# 指定需要查找的字符串
search_string = '+'

# 确保目标目录存在，不存在则创建
if not os.path.exists(target_directory):
    os.makedirs(target_directory)

# 遍历源目录中的文件
for filename in os.listdir(source_directory):
    # 检查文件名是否包含指定的字符串
    if search_string in filename:
        # 构建源文件的完整路径
        source_file_path = os.path.join(source_directory, filename)
        # 构建目标文件的完整路径
        target_file_path = os.path.join(target_directory, filename)
        # 将文件移动到目标目录
        shutil.move(source_file_path, target_file_path)
        print(f'文件 {filename} 已移动到 {target_directory}')
