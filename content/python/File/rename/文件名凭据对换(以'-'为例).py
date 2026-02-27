import os

# 指定路径A
path_A = r"C:\Users\chru\Desktop\rang"  # 请替换为您的路径A


# 遍历路径A中的所有文件和文件夹
for filename in os.listdir(path_A):
    # 构建文件的完整路径
    src_file = os.path.join(path_A, filename)
    # 检查是否为文件
    if os.path.isfile(src_file):
        # 分割文件名和扩展名
        base, extension = os.path.splitext(filename)
        # 分割文件名，找到'-'符号的位置
        parts = base.split('-')
        # 如果文件名中包含'-'
        if len(parts) > 1:
            # 将'-'左右两端的文字互换
            new_name = '-'.join(parts[1:] + parts[:1])
            # 构建新的文件名
            dst_file = os.path.join(path_A, new_name + extension)
            # 重命名文件
            os.rename(src_file, dst_file)
            print(f"文件 {filename} 已重命名为 {new_name + extension}")
       # else:
         #   print(f"文件 {filename} 不包含 '-'，不被重命名。")

"""
| 原文件名 | 重命名后 |
|----------|----------|
| `report-2023.pdf` | `2023-report.pdf` |
| `user-data-backup.zip` | `data-backup-user.zip` |
| `a-b-c.txt` | `b-c-a.txt` |


"""