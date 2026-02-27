#文件替换重命名
import os

# 定义一个字典，用于映射关键词到新名称
my_dict = {'A': 'a', '-1': 'ptsd'}

# 指定要重命名的目录
directory = r"C:\Users\chru\Desktop\1"

# 遍历目录中的所有文件和文件夹
for filename in os.listdir(directory):
    # 检查文件名是否在字典中映射的关键词
    for old_key, new_value in my_dict.items():
        if old_key in filename:
            # 构建新的文件名
            new_filename = filename.replace(old_key, new_value)
            # 获取原始文件完整路径
            old_filepath = os.path.join(directory, filename)
            # 获取新的文件完整路径
            new_filepath = os.path.join(directory, new_filename)
            # 重命名文件
            os.rename(old_filepath, new_filepath)
            print(f'Renamed "{filename}" to "{new_filename}"')
            break  # 如果找到了关键词，就不需要继续检查其他关键词了

