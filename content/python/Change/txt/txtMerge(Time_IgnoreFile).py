import os
import re
from datetime import datetime

# 定义需要屏蔽的文件夹名称列表
IGNORE_FOLDERS = [
    ".git",
    "聊天记录",
    "未知时间"
]

def find_txt_files(folder_path):
    """递归查找所有txt文件，跳过屏蔽的文件夹"""
    txt_files = []
    
    for root, dirs, files in os.walk(folder_path):
        # 在遍历时移除需要屏蔽的文件夹，避免进入这些目录
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]
        
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

def merge_all_txt_files(root_folder, output_file="merged.txt"):
    """合并根目录下所有文件夹中的txt文件，跳过屏蔽的文件夹"""
    # 获取根目录下所有txt文件路径（包括子文件夹，但跳过屏蔽文件夹）
    txt_files = find_txt_files(root_folder)
    
    if not txt_files:
        print(f"在 {root_folder} 及其子文件夹中未找到txt文件")
        return
    
    # 存储文件信息：(日期, 文件路径, 文件内容, 文件名, 相对路径)
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
        
        # 计算相对路径，用于在合并文件中显示文件位置
        relative_path = os.path.relpath(file_path, root_folder)
            
        file_data.append((file_date, file_path, content, filename, relative_path))
    
    if not file_data:
        print(f"在 {root_folder} 及其子文件夹中未找到包含有效日期的txt文件")
        return
    
    # 按日期排序
    file_data.sort(key=lambda x: x[0])
    
    # 写入合并文件
    with open(output_file, 'w', encoding='utf-8') as out:
        # 写入合并信息头部
        out.write(f"合并时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"源目录: {root_folder}\n")
        out.write(f"合并文件数量: {len(file_data)}\n")
        out.write(f"屏蔽的文件夹: {', '.join(IGNORE_FOLDERS)}\n")
        out.write("=" * 60 + "\n\n")
        
        for _, _, content, filename, relative_path in file_data:
            # 去除文件名中的.txt扩展名
            display_name = os.path.splitext(filename)[0]
            
            # 写入文件名分隔线
            out.write(f"\n\n{'=' * 60}\n")
            out.write(f"文件: {display_name}\n")
            out.write(f"位置: {relative_path}\n")
            out.write(f"{'=' * 60}\n\n")
            # 写入文件内容
            out.write(content)
            out.write('\n')  # 文件末尾添加换行
    
    print(f"已合并 {len(file_data)} 个文件到 {output_file}")
    print(f"跳过了以下文件夹: {', '.join(IGNORE_FOLDERS)}")

if __name__ == "__main__":
    # 使用当前目录作为根目录
    current_directory = os.getcwd()
    print(f"当前工作目录: {current_directory}")
    
    # 检查当前目录下是否有文件夹
    items = os.listdir(current_directory)
    folders = [item for item in items if os.path.isdir(os.path.join(current_directory, item))]
    
    if not folders:
        print("当前目录下没有找到任何文件夹")
    else:
        print(f"找到 {len(folders)} 个文件夹: {', '.join(folders)}")
    
    # 合并当前目录及其所有子文件夹中的txt文件（跳过屏蔽文件夹）
    output_name = "merged_all.txt"
    merge_all_txt_files(current_directory, output_name)
    
    print("\n合并完成!")