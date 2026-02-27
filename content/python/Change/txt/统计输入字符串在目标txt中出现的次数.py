import os

# 输入要搜索的字符串
input_string = "code"

# 输入要搜索的目录路径（变量形式存储）
search_dir = r"C:\Users\chru\Desktop\task"

# 初始化结果列表（存储出现次数大于0的文件路径）
results = []

# 遍历目录及所有子目录
for root, dirs, files in os.walk(search_dir):
    for file_name in files:
        # 检查文件扩展名是否为.txt或.md
        if file_name.endswith(('.txt', '.md')):
            file_path = os.path.join(root, file_name)
            try:
                # 读取文件内容并统计字符串出现次数
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    count = content.count(input_string)
                    
                    # 如果出现次数大于0，记录文件路径
                    if count > 0:
                        results.append((file_path, count))
            except Exception as e:
                print(f"无法读取文件 {file_path}: {str(e)}")

# 输出结果（只显示出现次数大于0的文件路径）
if results:
    print("\n找到以下包含该字符串的文件：")
    for file_path, count in results:
        print(f"文件路径: {file_path} (出现次数: {count})")
else:
    print(f"\n在 {search_dir} 及其子目录中未找到包含该字符串的文本文件")