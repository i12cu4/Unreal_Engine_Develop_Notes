import os
import shutil

def process_folders(source_dir, target_dir):
    """
    处理指定目录下的所有文件夹，满足条件时移动文件并删除源文件夹
    
    参数:
        source_dir (str): 要扫描的源目录路径
        target_dir (str): 目标存放目录路径
    """
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)

    # 遍历源目录中的所有条目
    for entry in os.scandir(source_dir):
        if entry.is_dir():
            folder_path = entry.path
            folder_name = entry.name
            
            try:
                # 获取目录中的所有条目
                contents = list(os.scandir(folder_path))
                
                # 检查是否只有一个文件
                if len(contents) == 1:
                    item = contents[0]
                    if item.is_file():
                        # 处理文件扩展名
                        file_ext = os.path.splitext(item.name)[1]
                        new_name = f"{folder_name}{file_ext}"
                        dest_path = os.path.join(target_dir, new_name)

                        # 移动并重命名文件
                        shutil.move(item.path, dest_path)
                        print(f"Moved: {item.name} -> {dest_path}")

                        # 删除空目录
                        os.rmdir(folder_path)
                        print(f"Deleted empty directory: {folder_path}")
            except Exception as e:
                print(f"Error processing {folder_path}: {str(e)}")

if __name__ == "__main__":
    # 使用示例
    source_directory = r"E:\Download\UE5资源整合"  # 替换为源目录路径
    target_directory = r"E:\Download\cgtall.com"  # 替换为目标目录路径
    
    process_folders(source_directory, target_directory)

"""
打开 Tree 文件夹 → 里面只有1个文件 →
→ 把 model_v2.fbx 拿出来 → 改名成 Tree.fbx → 放进 cgtall.com 文件夹 → 删除空的 Tree 文件夹

打开 Rock 文件夹 → 有2个文件 → 不动！跳过！

打开 Grass 文件夹 → 里面只有1个文件 →
→ 把 material.mat 拿出来 → 改名成 Grass.mat → 放进 cgtall.com → 删除空的 Grass
"""