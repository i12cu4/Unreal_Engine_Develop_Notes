#文件名查重与迁移(兼容大小写)
import os
import shutil

# 定义文件夹路径
path_A = r"D:\music"  # 请替换为你的A目录路径
path_B = r"C:\Users\chru\Downloads\Cache\Cache"  # 请替换为你的B目录路径
#path_B = r"D:\newmusic"  # 请替换为你的B目录路径
path_C = r"C:\Users\chru\Desktop\temps"  # 请替换为你的C目录路径


# 获取A文件夹下的所有文件名（英文字母改为小写）
files_A = [os.path.basename(f).lower() for f in os.listdir(path_A) if os.path.isfile(os.path.join(path_A, f))]

# 获取B文件夹下的所有文件名（英文字母改为小写）
files_B = [os.path.basename(f).lower() for f in os.listdir(path_B) if os.path.isfile(os.path.join(path_B, f))]

# 找到A和B的交集
files_common = set(files_A) & set(files_B)

# 创建C文件夹（如果还不存在）
if not os.path.exists(path_C):
    os.makedirs(path_C)

# 遍历A文件夹下的文件，如果文件名小写后存在于交集容器中，则移动文件到C文件夹
for file_A in os.listdir(path_A):
    if os.path.isfile(os.path.join(path_A, file_A)):
        file_name_lower = os.path.basename(file_A).lower()
        if file_name_lower in files_common:
            shutil.move(os.path.join(path_A, file_A), os.path.join(path_C, file_A))
            print(f"文件 {file_A} 已移动到 {path_C}")
