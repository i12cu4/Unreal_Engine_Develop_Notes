import os

# 输入字符串
search_string = input("请输入要搜索的字符串：")

# 获取当前目录
current_dir = os.getcwd()

# 遍历根目录
for foldername, subfolders, filenames in os.walk(current_dir):
    for filename in filenames:
        if filename.endswith('.txt'):
            # 拼接完整的文件路径
            filepath = os.path.join(foldername, filename)
            # 打开并搜索字符串
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                if search_string in file.read():
                    print(f"字符串'{search_string}'在文件'{filename}'中找到。")


print("搜索完成。")