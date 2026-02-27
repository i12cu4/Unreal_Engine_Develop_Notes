import os

def remove_newlines(directory):
    # 遍历指定目录
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.txt'):
                # 拼接完整的文件路径
                filepath = os.path.join(foldername, filename)
                # 打开并读取文件内容
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # 去除换行符
                    content_without_newlines = content.replace('\n', '')
                    # 写回文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content_without_newlines)
                print(f"文件'{filename}'中的换行符已去除。")

# 输入目录路径
directory_path = os.getcwd()
remove_newlines(directory_path)
print("操作完成。")
