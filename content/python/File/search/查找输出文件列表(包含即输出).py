# 配合"输出文件列表(包含子目录,Markdown版本)(不分离版)"文件使用

import os

# 定义文件路径
file_paths = [
    r"D:\Download\MovepackList\fileoutputE1.md",
    r"D:\Download\MovepackList\fileoutputE2.md",
    r"D:\Download\MovepackList\fileoutputE3.md",
    r"D:\Download\MovepackList\fileoutputE4.md",
]

# 用于存储文件名及其来源的字典
file_dict = {}


# 处理每个文件并更新字典
def process_file(file_path, source):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            # 从markdown表格格式中提取文件名
            parts = line.strip().split("|")
            if len(parts) > 2:
                filename = parts[1].strip()
                if filename in file_dict:
                    file_dict[filename].append(source)
                else:
                    file_dict[filename] = [source]


# 处理每个文件
for i, path in enumerate(file_paths):
    process_file(path, f"FileoutputE{i+1}")

# 筛选出在多个文件中出现的文件名
duplicates = {
    filename: sources for filename, sources in file_dict.items() if len(sources) > 1
}

# 将重复的文件输出到新的markdown文件
output_path = r"D:\Download\MovepackList\duplicate_files.md"
with open(output_path, "w", encoding="utf-8") as output_file:
    output_file.write("# Duplicate Files\n\n")
    output_file.write("| Filename | Exists In |\n")
    output_file.write("| --- | --- |\n")
    for filename, sources in duplicates.items():
        output_file.write(f"| {filename} | {', '.join(sources)} |\n")

print(f"Duplicate files have been written to {output_path}")
