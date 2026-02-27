import os
import shutil

def delete_empty_folders(startpath):
    for root, dirs, files in os.walk(startpath, topdown=False):
        if not dirs and not files:
            os.rmdir(root)
            print(f'Deleted empty folder: {root}')

# 指定要清理的目录路径
startpath = r'C:\Users\chru\Desktop\temp'

# 调用函数
delete_empty_folders(startpath)
