import os
import shutil

def get_filename_without_extension(filename):
    return os.path.splitext(filename)[0]

def add_string_to_filename(filename, string):
    return filename + string

def move_files_if_exists(src_path, dst_path, strings_to_add):
    # 获取源文件夹中的文件列表
    files_in_src = os.listdir(src_path)
    
    for filename in files_in_src:
        # 去掉文件扩展名
        base_filename = get_filename_without_extension(filename)
        
        # 给定的字符串添加到文件名后面
        new_filename = add_string_to_filename(base_filename, strings_to_add)
        
        # 构造新的文件名（带扩展名）
        new_filename_with_ext = f"{new_filename}{os.path.splitext(filename)[1]}"
        
        # 检查新的文件名是否存在于源文件夹中
        new_file_path = os.path.join(src_path, new_filename_with_ext)
        if os.path.isfile(new_file_path):
            # 如果存在，则移动文件到目标文件夹
            dst_file_path = os.path.join(dst_path, new_filename_with_ext)
            shutil.move(new_file_path, dst_file_path)
            print(f"Moved {new_file_path} to {dst_file_path}")

# 示例用法

src_path = r"D:\tempmuc"
dst_path = r"C:\Users\chru\Desktop\del"
strings=["1","2","3","4","5","6","7","8","9","(live)","(Hidden Track)","(Remix)","(ENG VER.)","(Korean Version)","(Special Ver.)","(不插电版)","(Live)","(Karaoke ver.)","(Japanese Ver.)","(girls ver.)","(girls ver.)","(MV版)"]
for strings_to_add in strings:
    move_files_if_exists(src_path, dst_path, strings_to_add)
