import os
import shutil

# 指定路径A和B
path_A = r'C:\Users\chru\Desktop\rang'  # 请替换为您的路径A
path_B = r'C:\Users\chru\Desktop\why'  # 请替换为您的路径B

# 检查路径是否存在
if not os.path.exists(path_B):
    os.makedirs(path_B)

# 遍历路径A中的所有文件和文件夹
for filename in os.listdir(path_A):
    # 检查文件名中'-'符号的数量
    if filename.count('-') > 1:
        # 构建文件的完整路径
        src_file = os.path.join(path_A, filename)
        # 移动文件到路径B，注意检查是否为文件
        if os.path.isfile(src_file):
            dst_file = os.path.join(path_B, filename)
            shutil.move(src_file, dst_file)
            print(f"文件 {filename} 已移动到 {path_B}")
        #else:
           # print(f"{filename} 不是文件，不被移动。")
