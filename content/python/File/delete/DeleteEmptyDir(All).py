import os
import shutil

def delete_empty_folders_recursive(startpath):
    while True:
        for root, dirs, files in os.walk(startpath, topdown=True):
            if not dirs and not files:
                os.rmdir(root)
                print(f'Deleted empty folder: {root}')
                
        # 检查是否有空的文件夹存在，如果没有，则退出循环
        if not os.listdir(startpath):
            break

# 指定要清理的目录路径
startpath = r'C:\Users\chru\Desktop\temp'

# 调用函数
delete_empty_folders_recursive(startpath)
