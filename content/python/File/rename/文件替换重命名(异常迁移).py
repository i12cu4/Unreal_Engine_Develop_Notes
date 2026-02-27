import os
import shutil

# 指定路径
path_A = r'D:\newmusic2024.3.6'  # 请替换为实际的路径A
string_B = '.mp3'  # 需要替换的字符串B
string_C = '.flac'  # 用来替换字符串B的新字符串C
path_D = r'C:\Users\chru\Desktop\del'  # 请替换为实际的路径D

# 检查D目录是否存在，如果不存在则创建
if not os.path.exists(path_D):
    os.makedirs(path_D)

# 遍历路径A下的所有文件和目录
for filename in os.listdir(path_A):
    # 构建旧文件名和新的文件名
    old_name = os.path.join(path_A, filename)
    if string_B in filename:
        # 替换字符串B
        new_name = filename.replace(string_B, string_C)
        new_path = os.path.join(path_A, new_name)
        
        # 尝试重命名文件
        try:
            os.rename(old_name, new_path)
            #print(f"文件 '{old_name}' 已重命名为 '{new_path}'")
        except OSError as e:
            # 如果重命名失败，将文件移动到路径D
            shutil.move(old_name, os.path.join(path_D, new_name))
            print(f"重命名 '{old_name}' 时出错，已移动到 '{path_D}'")
    #else:
        #print(f"文件 '{filename}' 不包含字符串 '{string_B}'，忽略。")

print("操作完成。")
