#文件名查重与迁移(兼容扩展名和大小写)
import os
import shutil

# 定义源文件夹和目标文件夹路径
A_folder = r"D:\music"
B_folder = r"C:\Users\chru\Downloads\Cache\Cache"
C_folder = r"C:\Users\chru\Desktop\temp"

# 获取A文件夹下的所有文件名（去除扩展名，英文字母改为小写）
# 使用os.path.splitext分离文件名和扩展名，并使用os.path.basename获取文件名
files_A = [(os.path.splitext(os.path.basename(f))[0]).lower() for f in os.listdir(A_folder) if os.path.isfile(os.path.join(A_folder, f))]

# 获取B文件夹下的所有文件名（去除扩展名，英文字母改为小写）
files_B = [(os.path.splitext(os.path.basename(f))[0]).lower() for f in os.listdir(B_folder) if os.path.isfile(os.path.join(B_folder, f))]

# 找到A和B的交集
files_common = set(files_A) & set(files_B)

# 创建C文件夹（如果还不存在）
if not os.path.exists(C_folder):
    os.makedirs(C_folder)

# 遍历A文件夹下的文件，如果文件名小写后存在于交集容器中，则移动文件到C文件夹
for file_A in os.listdir(A_folder):
    if os.path.isfile(os.path.join(A_folder, file_A)):
        # 分离文件名和扩展名，并去除扩展名
        file_name_lower = (os.path.splitext(os.path.basename(file_A))[0]).lower()
        if file_name_lower in files_common:
            shutil.move(os.path.join(A_folder, file_A), os.path.join(C_folder, file_A))
            print(f"文件 {file_A} 已移动到 {C_folder}")
            