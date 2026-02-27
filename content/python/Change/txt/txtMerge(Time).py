import os
import re
from datetime import datetime

def find_txt_files(folder_path):
    """递归查找所有txt文件"""
    txt_files = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith('.txt'):
                file_path = os.path.join(root, filename)
                txt_files.append(file_path)
    return txt_files

def extract_date_from_filename(filename):
    """从文件名中提取日期"""
    # 匹配YYYY.MM.DD或YYYY.M.D格式
    match = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', filename)
    if match:
        year, month, day = map(int, match.groups())
        try:
            return datetime(year, month, day)
        except ValueError:
            return None
    return None

def merge_txt_files(folder_path, output_file="merged.txt"):
    # 获取所有txt文件路径
    txt_files = find_txt_files(folder_path)
    
    if not txt_files:
        print("未找到txt文件")
        return
    
    # 存储文件信息：(日期, 文件路径, 文件名)
    file_data = []
    
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        file_date = extract_date_from_filename(filename)
        
        if not file_date:
            continue  # 跳过不含有效日期的文件
            
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"读取文件 {file_path} 失败: {e}")
            continue
            
        file_data.append((file_date, file_path, content, filename))
    
    if not file_data:
        print("未找到包含有效日期的txt文件")
        return
    
    # 按日期排序
    file_data.sort(key=lambda x: x[0])
    
    # 写入合并文件
    with open(output_file, 'w', encoding='utf-8') as out:
        for _, _, content, filename in file_data:
            # 去除文件名中的.txt扩展名
            display_name = os.path.splitext(filename)[0]
            
            # 写入文件名分隔线
            out.write(f"\n\n{'=' * 50}\n")
            out.write(f"文件: {display_name}\n")
            out.write(f"{'=' * 50}\n\n")
            # 写入文件内容
            out.write(content)
            out.write('\n')  # 文件末尾添加换行
    
    print(f"已合并 {len(file_data)} 个文件到 {output_file}")

if __name__ == "__main__":
    target_folder = r"C:\Users\chru\Desktop\Crown_of_Tokamak"
    if os.path.isdir(target_folder):
        output_name = "merged.txt"
        merge_txt_files(target_folder, output_name)
    else:
        print("错误：无效的文件夹路径")