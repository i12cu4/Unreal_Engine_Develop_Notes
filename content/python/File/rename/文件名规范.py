import os
import shutil

# 设置您要重命名的文件夹路径
folder_path = r"D:\newmusic"

# 设置文件扩展名
extension = '.mp3'

# 设置无法重命名时文件要移动到的路径
move_folder_path = r"D:\newmusic\moved"

# 确保移动文件夹存在
if not os.path.exists(move_folder_path):
    os.makedirs(move_folder_path)

# 遍历文件夹中的所有文件
for file in os.listdir(folder_path):
    # 检查文件是否具有指定的扩展名
    if file.endswith(extension):
        # 构建新的文件名
        new_name = file.replace(' - ', '-')
        # 获取原文件的完整路径
        old_file = os.path.join(folder_path, file)
        # 获取新文件的完整路径
        new_file = os.path.join(folder_path, new_name)
        try:
            # 重命名文件
            os.rename(old_file, new_file)
            # 打印成功重命名的文件
            #print(f'Renamed "{file}" to "{new_name}"')
        except OSError:
            # 如果重命名失败，将文件移动到另一个路径
            move_file = os.path.join(move_folder_path, new_name)
            shutil.move(old_file, move_file)
            # 打印重命名失败并将文件移动的消息
            print(f'Failed to rename "{file}", moved to "{move_file}"')

print('All files have been processed.')
