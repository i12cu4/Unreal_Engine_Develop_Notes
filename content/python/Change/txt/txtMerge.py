import os

def merge_txt_files(root_dir):
    # 列出目录中的所有.txt文件
    txt_files = [f for f in os.listdir(root_dir) if os.path.splitext(f)[1] == '.txt']
    
    # 逐个打开并读取.txt文件
    merged_content = ''
    for txt_file in txt_files:
        #merged_content+=txt_file.split('.')[0]+'\n'
        with open(os.path.join(root_dir, txt_file), 'r', encoding='utf-8') as f:
            merged_content += f.read() # + '\n'  # 将文件内容合并，每个文件内容后添加一个换行符

    # 将合并后的内容写入新的.txt文件
    with open(os.path.join(root_dir, 'merged.txt'), 'w', encoding='utf-8') as f:
        f.write(merged_content)

# 调用函数，传入脚本根目录
root_dir = r"C:\Users\chru\Desktop\Unreal_Engine_Develop_Notes\content\杂谈\托卡马克之冠\知乎主页" #os.path.dirname(__file__)
merge_txt_files(root_dir)

print('done to merge txt')
