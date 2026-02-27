# 文件查重 输出双表格 1.文件大小相同 2.文件大小不同
import os

# 定义文件路径
filepaths = [
    r"D:\Download\MovepackList\fileoutputE1.md",
    r"D:\Download\MovepackList\fileoutputE2.md",
    r"D:\Download\MovepackList\fileoutputE4.md",
    r"D:\Download\MovepackList\fileoutputE3.md",
]
#该文件是同路径下  "输出文件列表(包含子目录,Markdown版本)(不分离版).py" 生成的

# 用于存储文件名及其大小和来源的字典
file_info = {}

# 处理每个文件并更新字典
for filepath in filepaths:
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            # 从markdown表格格式中提取文件名和大小
            parts = line.strip().split("|")
            if len(parts) > 2:
                filename = parts[1].strip()
                size_kb = parts[2].strip()
                if filename not in file_info:
                    file_info[filename] = []
                file_info[filename].append((size_kb, filepath))

# 查找重复的文件名
duplicates_same_size = {}
duplicates_diff_size = {}

for filename, sizes in file_info.items():
    if len(sizes) > 1:
        # 检查所有大小是否相同
        first_size = sizes[0][0]
        if all(size[0] == first_size for size in sizes):
            duplicates_same_size[filename] = [size[1] for size in sizes]
        else:
            duplicates_diff_size[filename] = [size[1] for size in sizes]

# 输出结果到新的Markdown文件
output_path = r"D:\Download\MovepackList\duplicate_files2.md"
with open(output_path, "w", encoding="utf-8") as output_file:
    # 输出文件大小相同的重复文件
    output_file.write("# Files with Same Size\n")
    output_file.write("| Filename | Exists In |\n")
    output_file.write("| --- | --- |\n")
    for filename, sources in duplicates_same_size.items():
        output_file.write(f"| {filename} | {', '.join(sources)} |\n")

    # 输出文件大小不相同的重复文件
    if duplicates_diff_size:
        output_file.write("\n# Files with Different Sizes\n")
        output_file.write("| Filename | Exists In |\n")
        output_file.write("| --- | --- |\n")
        for filename, sources in duplicates_diff_size.items():
            output_file.write(f"| {filename} | {', '.join(sources)} |\n")

print(f"Duplicate files have been written to {output_path}")
