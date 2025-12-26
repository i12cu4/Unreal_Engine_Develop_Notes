import os
import sys

def remove_all_kgm_from_filename(filename):
    """
    从文件名中删除所有".kgm"字符串
    包括文件名和扩展名中的所有部分
    """
    # 删除文件名中的所有".kgm"字符串
    new_filename = filename.replace(".kgm", "")
    
    # 如果删除后文件名为空，使用默认名称
    if not new_filename:
        return "renamed_file"
    
    return new_filename

def process_file(file_path):
    """
    处理单个文件：删除文件名中的所有".kgm"字符串
    """
    # 获取文件目录和原始文件名
    directory = os.path.dirname(file_path)
    original_filename = os.path.basename(file_path)
    
    # 生成新文件名
    new_filename = remove_all_kgm_from_filename(original_filename)
    
    # 如果文件名没有变化，跳过
    if original_filename == new_filename:
        return False
    
    # 构建完整的新文件路径
    new_file_path = os.path.join(directory, new_filename)
    
    # 检查新文件名是否已存在
    if os.path.exists(new_file_path):
        print(f"目标文件已存在，跳过: {original_filename}")
        return False
    
    # 重命名文件
    try:
        os.rename(file_path, new_file_path)
        print(f"已重命名: {original_filename} -> {new_filename}")
        return True
    except Exception as e:
        print(f"重命名失败 {original_filename}: {e}")
        return False

def process_directory(directory_path):
    """
    处理目录：递归遍历目录中的所有文件
    """
    renamed_count = 0
    
    for root, dirs, files in os.walk(directory_path):
        # 不处理目录名，只处理文件名
        for file in files:
            file_path = os.path.join(root, file)
            if process_file(file_path):
                renamed_count += 1
    
    return renamed_count

def process_paths(paths):
    """
    处理所有拖拽的路径
    """
    if not paths:
        print("请将文件或文件夹拖拽到本程序")
        print("")
        print("功能说明:")
        print("  删除所有文件名中的所有\".kgm\"字符串")
        print("  包括扩展名中的\".kgm\"也会被删除")
        print("  例如:")
        print("    song.kgm.flac -> song.flac")
        print("    test.kgm -> test")
        print("    file.kgm.kgm.txt -> file.txt")
        print("")
        input("按回车键退出...")
        return
    
    print("文件名清理工具 - 删除文件名中的所有\".kgm\"字符串")
    print("=" * 60)
    
    total_renamed = 0
    total_processed = 0
    
    for path in paths:
        if not os.path.exists(path):
            print(f"路径不存在，跳过: {path}")
            continue
        
        print(f"处理路径: {path}")
        
        if os.path.isfile(path):
            # 处理单个文件
            total_processed += 1
            if process_file(path):
                total_renamed += 1
        elif os.path.isdir(path):
            # 处理文件夹（递归遍历）
            print(f"递归遍历文件夹: {path}")
            renamed_in_dir = process_directory(path)
            total_renamed += renamed_in_dir
            # 统计处理的文件数量（通过遍历文件夹）
            file_count = 0
            for root, dirs, files in os.walk(path):
                file_count += len(files)
            total_processed += file_count
        else:
            print(f"未知类型，跳过: {path}")
    
    print("=" * 60)
    print(f"处理完成!")
    print(f"  总处理文件数: {total_processed}")
    print(f"  重命名文件数: {total_renamed}")
    print(f"  未更改文件数: {total_processed - total_renamed}")
    print("")
    input("按回车键退出...")

def main():
    """
    主函数入口
    """
    # 获取拖拽到程序的路径
    paths = sys.argv[1:]
    
    # 处理路径
    process_paths(paths)

if __name__ == "__main__":
    main()