import os

def replace_content(directory, old_content, new_content):
    # 遍历指定目录
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.txt'):
                # 拼接完整的文件路径
                filepath = os.path.join(foldername, filename)
                # 打开并读取文件内容
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # 替换指定的内容
                    content = content.replace(old_content, new_content)
                    # 写回文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                print(f"文件'{filename}'中的'{old_content}'已替换为'{new_content}'。")

# 输入目录路径
directory_path = os.getcwd()
# 输入要替换的字符串
old_content = input("请输入要替换的内容：")
# 输入替换后的字符串
new_content = input("请输入新的内容：")
replace_content(directory_path, old_content, new_content)
print("操作完成。")
