#文件名查重与迁移(兼容扩展名)
import os
import shutil

# 定义源文件夹和目标文件夹路径
A_folder = r"D:\music"
B_folder = r"D:\newmusic"
#B_folder=r"C:\Users\chru\Downloads\Cache\Cache"
C_folder = r"C:\Users\chru\Desktop\temp"

# 获取A文件夹中的所有文件名（去除扩展名）
files_in_A = set()
for filename in os.listdir(A_folder):
    if filename.endswith('.flac'):
        files_in_A.add(os.path.splitext(filename)[0])

# 获取B文件夹中的所有文件名（去除扩展名）
files_in_B = set()
for filename in os.listdir(B_folder):
    if filename.endswith('.mp3'):
        files_in_B.add(os.path.splitext(filename)[0])

# 找出两个文件夹中相同的文件名
common_files = files_in_A.intersection(files_in_B)

# 移动A文件夹中相同的文件到C文件夹
for file_name in common_files:
    # 获取A文件夹中文件的完整路径
    file_in_A_path = os.path.join(A_folder, file_name + '.flac')
    # 获取B文件夹中文件的完整路径（可选，如果你需要这个）
    # file_in_B_path = os.path.join(B_folder, file_name + '.mp3')
    
    # 创建目标路径
    dest_path = os.path.join(C_folder, file_name + '.flac')
    
    # 移动文件
    shutil.move(file_in_A_path, dest_path)
    print(f'Moved {file_name} from A to C')

print('Done!')
