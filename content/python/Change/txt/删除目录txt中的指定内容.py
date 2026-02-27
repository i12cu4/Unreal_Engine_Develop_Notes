import os

def remove_content(directory, content_to_remove):
    # 遍历指定目录
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.txt'):
                # 拼接完整的文件路径
                filepath = os.path.join(foldername, filename)
                # 打开并读取文件内容
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # 删除指定的内容
                    content = content.replace(content_to_remove, '')
                    # 写回文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                print(f"文件'{filename}'中的'{content_to_remove}'已删除。")

# 输入目录路径
directory_path = os.getcwd()
# 输入要删除的字符串
content_to_remove = input("请输入要删除的内容：")
remove_content(directory_path, content_to_remove)
print("操作完成。")
