import os
import shutil

# 存入字符串列表
strings_to_search = ['(Instrumental)','instrumental','(INST','Inst)','inst)','Inst.)','inst.)','(Inst','(inst',"预告版)","片段版)","(现场版)","现场)","铃声版)",'铃声)','片段)','(Teaser)','Intro','伴奏)','(伴奏版)']
# 给定的文件路径A和B
source_directory = r"D:\tempmuc"#r"C:\Users\chru\Downloads\Cache\Cache"  # 请替换为源文件夹路径
destination_directory = r"C:\Users\chru\Desktop\del"  # 请替换为目标文件夹路径

# 检查目标目录是否存在，如果不存在则创建
if not os.path.exists(destination_directory):
    os.makedirs(destination_directory)

# 遍历源目录中的所有文件
for filename in os.listdir(source_directory):
    # 检查文件名是否包含给定的字符串之一
    for string in strings_to_search:
        if string in filename:
            # 构建源文件和目标文件的完整路径
            source_file_path = os.path.join(source_directory, filename)
            destination_file_path = os.path.join(destination_directory, filename)

            # 移动文件
            shutil.move(source_file_path, destination_file_path)
            print(f'文件 {filename} 已移动到 {destination_directory}')
            break  # 找到匹配的字符串后跳出循环
