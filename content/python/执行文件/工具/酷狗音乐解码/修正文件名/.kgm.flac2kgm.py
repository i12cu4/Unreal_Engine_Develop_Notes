import os
import sys

def process_file(file_path):
    """
    处理单个文件：将 .kgm.flac 文件重命名为 .kgm 文件
    """
    # 检查文件是否以 .kgm.flac 结尾
    if file_path.endswith('.kgm.flac'):
        # 获取文件名（不含路径）
        file_name = os.path.basename(file_path)
        # 获取目录路径
        dir_path = os.path.dirname(file_path)
        
        # 构建新文件名：去掉 .flac 后缀
        new_file_name = file_name[:-5]  # 去掉最后的 .flac (5个字符)
        
        # 构建完整的新文件路径
        new_file_path = os.path.join(dir_path, new_file_name)
        
        # 重命名文件
        try:
            os.rename(file_path, new_file_path)
            print(f"已重命名: {file_name} -> {new_file_name}")
        except Exception as e:
            print(f"重命名失败 {file_name}: {e}")

def process_directory(directory_path):
    """
    处理目录：遍历目录中的所有文件
    """
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            process_file(file_path)

def main():
    """
    主函数：处理拖拽到程序的路径
    """
    # 获取所有拖拽到程序的路径
    paths = sys.argv[1:]
    
    if not paths:
        print("请将文件或文件夹拖拽到本程序")
        input("按回车键退出...")
        return
    
    print(f"开始处理 {len(paths)} 个路径...")
    
    for path in paths:
        # 检查路径是否存在
        if not os.path.exists(path):
            print(f"路径不存在: {path}")
            continue
        
        # 判断是文件还是文件夹
        if os.path.isfile(path):
            print(f"处理文件: {path}")
            process_file(path)
        elif os.path.isdir(path):
            print(f"处理文件夹: {path}")
            process_directory(path)
        else:
            print(f"未知类型: {path}")
    
    print("\n处理完成!")
    input("按回车键退出...")

if __name__ == "__main__":
    main()