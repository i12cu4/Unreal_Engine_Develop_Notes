import os
import re

# 指定路径
path = r"C:\Users\chru\Desktop\1"

# 遍历指定路径下的所有文件
for filename in os.listdir(path):
    # 检查文件扩展名是否为.mp3
    if filename.endswith('.mp3'):
        # 使用正则表达式查找不在空格旁边的连字符
        # 这个正则表达式会匹配任何位置的连字符，但不会匹配位于空格旁边的连字符
        pattern = re.compile(r'(?<!\s)-(?!\s)')
        
        # 使用正则表达式进行替换，将连字符替换为' - '
        new_filename = pattern.sub(' - ', filename)
        
        # 如果新的文件名与原文件名不同，则进行重命名
        if new_filename != filename:
            # 获取原文件的完整路径
            old_file = os.path.join(path, filename)
            # 获取新文件的完整路径
            new_file = os.path.join(path, new_filename)
            
            # 重命名文件
            os.rename(old_file, new_file)
            print(f'Renamed "{filename}" to "{new_filename}"')

print(' Renaming complete. ')
