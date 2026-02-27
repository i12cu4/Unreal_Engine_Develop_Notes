import os
import shutil
import re

# 定义文件夹A和B的路径
folder_a = r"D:\newmusic"
folder_b = r"C:\Users\chru\Desktop\del"

# 检查路径是否存在
if not os.path.exists(folder_a) or not os.path.exists(folder_b):
    print(f"文件夹A或文件夹B不存在： {folder_a} 或 {folder_b}")
    exit()

# 遍历文件夹A中的所有文件和文件夹
for filename in os.listdir(folder_a):
    # 检查文件名中是否包含括号
    if '(' in filename and ')' in filename:
        # 使用正则表达式去除括号及其内部内容
        base_filename_without_brackets = re.sub(r'\([^)]*\)', '', filename)
        # 检查去掉括号后的文件名是否存在
        if os.path.exists(os.path.join(folder_a, base_filename_without_brackets)):
            # 移动文件到文件夹B
            shutil.move(os.path.join(folder_a, filename), os.path.join(folder_b, filename))
            print(f"文件 {filename} 已移动到 {folder_b}")
        #else:
            #print(f"文件 {filename} 存在括号，但去掉括号后的文件 {base_filename_without_brackets} 不存在于文件夹A中")

"""
| 文件夹 A 中的原始项       | 去括号后名称     | 文件夹 A 中是否存在该名称 | 操作结果                     |
|--------------------------|------------------|--------------------------|----------------------------|
| `report(final).pdf`      | `report.pdf`     | ✅ 存在 `report.pdf`     | ✅ 移动至文件夹 B           |
| `image (copy).png`       | `image .png`     | ❌ 不存在（有空格差异）  | ❌ 保留在 A（常见失效场景） |
| `data(2023).xlsx`        | `data.xlsx`      | ✅ 存在 `data.xlsx`      | ✅ 移动至文件夹 B           |
| `notes.txt`              | （无括号）       | -                        | ❌ 跳过                     |
| `project(old_version)`   | `project`        | ✅ 存在 `project` 文件夹 | ✅ 整个文件夹移至 B         |
| `song(live)(remix).mp3`  | `song.mp3`       | ✅ 存在 `song.mp3`       | ✅ 移动至文件夹 B           |
"""