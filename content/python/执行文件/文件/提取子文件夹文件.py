import os
import shutil
import send2trash
from collections import defaultdict

def move_files_to_target(source_path):
    """
    将指定路径下所有文件夹中的文件移动到目标路径，处理文件名冲突
    """
    # 存储已存在的文件名和大小
    existing_files = {}
    # 存储需要移动的文件信息
    files_to_move = []
    
    print(f"开始处理路径: {source_path}")
    
    # 第一步：收集目标路径中已存在的文件信息
    for item in os.listdir(source_path):
        item_path = os.path.join(source_path, item)
        if os.path.isfile(item_path):
            file_size = os.path.getsize(item_path)
            existing_files[item] = file_size
    
    # 第二步：收集所有子文件夹中的文件
    for root, dirs, files in os.walk(source_path):
        # 跳过根目录本身
        if root == source_path:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                files_to_move.append((file_path, file, file_size, root))
    
    if not files_to_move:
        print("未找到需要移动的文件")
        # 即使没有文件移动，也要删除空文件夹
        remove_empty_folders(source_path)
        return
    
    print(f"找到 {len(files_to_move)} 个需要移动的文件")
    
    # 第三步：处理文件移动
    moved_count = 0
    renamed_count = 0
    
    for file_path, filename, file_size, original_folder in files_to_move:
        target_path = os.path.join(source_path, filename)
        
        # 情况1：目标路径没有同名文件
        if filename not in existing_files:
            try:
                shutil.move(file_path, target_path)
                existing_files[filename] = file_size
                moved_count += 1
                print(f"移动: {file_path} -> {target_path}")
            except Exception as e:
                print(f"移动失败 {file_path}: {e}")
        
        # 情况2：目标路径有同名文件，但大小相同
        elif existing_files[filename] == file_size:
            try:
                # 直接覆盖
                shutil.move(file_path, target_path)
                moved_count += 1
                print(f"覆盖: {file_path} -> {target_path}")
            except Exception as e:
                print(f"覆盖失败 {file_path}: {e}")
        
        # 情况3：目标路径有同名文件，但大小不同
        else:
            new_filename = generate_unique_filename(source_path, filename, existing_files)
            new_target_path = os.path.join(source_path, new_filename)
            
            try:
                shutil.move(file_path, new_target_path)
                existing_files[new_filename] = file_size
                renamed_count += 1
                print(f"重命名移动: {file_path} -> {new_target_path}")
            except Exception as e:
                print(f"重命名移动失败 {file_path}: {e}")
    
    # 第四步：删除所有空文件夹
    remove_empty_folders(source_path)
    
    print(f"\n操作完成!")
    print(f"成功移动: {moved_count} 个文件")
    print(f"重命名移动: {renamed_count} 个文件")

def generate_unique_filename(directory, filename, existing_files):
    """
    生成唯一的文件名，避免冲突
    """
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name} ({counter}){ext}"
        if new_filename not in existing_files:
            return new_filename
        counter += 1

def remove_empty_folders(source_path):
    """
    删除所有空文件夹
    """
    print("\n正在删除空文件夹...")
    empty_folders = []
    
    # 从最深层开始遍历，确保先处理子文件夹
    for root, dirs, files in os.walk(source_path, topdown=False):
        # 跳过根目录
        if root == source_path:
            continue
            
        # 如果文件夹为空，则添加到待删除列表
        if not dirs and not files:
            empty_folders.append(root)
    
    if empty_folders:
        print(f"找到 {len(empty_folders)} 个空文件夹")
        
        # 显示前几个空文件夹作为示例
        max_display = 5
        for i, folder in enumerate(empty_folders[:max_display]):
            print(f"  {folder}")
        if len(empty_folders) > max_display:
            print(f"  ... 还有 {len(empty_folders) - max_display} 个空文件夹")
        
        # 自动删除空文件夹，不再询问确认
        deleted_count = 0
        for folder in empty_folders:
            try:
                send2trash.send2trash(folder)
                print(f"已删除空文件夹: {folder}")
                deleted_count += 1
            except Exception as e:
                print(f"删除空文件夹失败 {folder}: {e}")
        
        print(f"已删除 {deleted_count} 个空文件夹")
    else:
        print("未找到空文件夹")

def main():
    # 设置目标路径
    target_path = r"C:\Users\Administrator\Desktop\新建文件夹-251107-105946993\《读者》1981-2023年合集收藏版：42年经典精华，值得珍藏的心灵读物"  # 请修改为你的实际路径
    
    # 检查路径是否存在
    if not os.path.exists(target_path):
        print(f"错误: 路径 '{target_path}' 不存在")
        return
    
    # 检查路径是否是文件夹
    if not os.path.isdir(target_path):
        print(f"错误: '{target_path}' 不是文件夹")
        return
    
    # 确认操作
    print(f"即将处理路径: {target_path}")
    print("此操作将:")
    print("1. 将所有子文件夹中的文件移动到目标路径")
    print("2. 同名同大小文件将被覆盖")
    print("3. 同名不同大小文件将被重命名")
    print("4. 所有空文件夹将被自动删除")
    
    confirm = input("\n确认执行此操作？(y/n): ").lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    move_files_to_target(target_path)

if __name__ == "__main__":
    main()