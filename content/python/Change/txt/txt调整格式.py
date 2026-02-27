import os
import re

def reformat_text_files(directory_path):
    # 创建保存处理后文件的目录
    output_dir = os.path.join(directory_path, "reformatted")
    os.makedirs(output_dir, exist_ok=True)
    
    # 递归遍历目录中的所有文件
    for root, dirs, files in os.walk(directory_path):
        # 跳过输出目录本身
        if os.path.abspath(root) == os.path.abspath(output_dir):
            continue
            
        for filename in files:
            if filename.lower().endswith('.txt'):
                file_path = os.path.join(root, filename)
                
                # 计算相对路径用于输出目录结构
                rel_path = os.path.relpath(root, directory_path)
                if rel_path == ".":
                    rel_path = ""
                
                # 创建对应的输出子目录
                output_subdir = os.path.join(output_dir, rel_path)
                os.makedirs(output_subdir, exist_ok=True)
                
                # 读取文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='gbk') as file:
                            content = file.read()
                    except:
                        print(f"无法解码文件: {file_path}")
                        continue
                
                # 删除所有空白字符（包括空格、换行、制表符等）
                content = re.sub(r'\s+', '', content)
                
                # 按中文标点重新换行
                # 处理常见标点：句号、问号、感叹号、省略号、分号、逗号等
                content = re.sub(r'([。？！…；])([^”’])', r'\1\n\n\2', content)  # 后引号特殊情况处理
                content = re.sub(r'([。？！…；][”’])([^"])', r'\1\n\n\2', content)
                # content = re.sub(r'([，、])', r'\1\n', content)
                
                # 保存处理后的文件
                output_path = os.path.join(output_subdir, filename)
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"已处理: {os.path.join(rel_path, filename)}")

if __name__ == "__main__":
    target_directory = r"C:\Users\chru\Desktop\merge"
    
    if not os.path.isdir(target_directory):
        print("错误: 指定的路径不是目录或不存在")
    else:
        reformat_text_files(target_directory)
        print("\n处理完成! 所有文件已保存到'reformatted'目录中，保持原有目录结构")