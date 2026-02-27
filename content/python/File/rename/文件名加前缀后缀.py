import os

# ===== 用户配置区 =====
# 设置要处理的目录路径（可以是绝对路径或相对路径）
TARGET_DIRECTORY = r"C:\Users\chru\Desktop\Unreal_Engine_Develop_Notes\content\杂谈\托卡马克之冠\2024"  # 请替换为实际路径

# 设置要添加到文件名前面的前缀（可以为空字符串）
FILE_PREFIX = "2024."

# 设置要添加到文件扩展名之前的后缀（可以为空字符串）
FILE_SUFFIX = ""

# 安全设置：是否跳过确认直接执行（True为直接执行，False为需要确认）
SKIP_CONFIRMATION = True
# ===== 配置结束 =====

def rename_files(directory, prefix, suffix):
    """
    递归重命名目录及其子目录中的所有文件
    :param directory: 要处理的根目录
    :param prefix: 要添加到文件名前面的字符串
    :param suffix: 要添加到文件扩展名之前的字符串
    """
    # 计数器
    renamed_count = 0
    skipped_count = 0
    errors = []
    
    print(f"\n开始处理目录: {directory}")
    print(f"命名规则: '{prefix}' + 原文件名 + '{suffix}' + 扩展名")
    print("=" * 50)
    
    # 递归遍历所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # 获取文件完整路径
            file_path = os.path.join(root, filename)
            
            # 分离文件名和扩展名
            name_part, ext_part = os.path.splitext(filename)
            
            # 构建新文件名
            new_name = f"{prefix}{name_part}{suffix}{ext_part}"
            new_path = os.path.join(root, new_name)
            
            # 如果新文件名与旧文件名相同，则跳过
            if new_name == filename:
                skipped_count += 1
                continue
            
            try:
                # 重命名文件
                os.rename(file_path, new_path)
                print(f"重命名: {filename} -> {new_name}")
                renamed_count += 1
            except Exception as e:
                error_msg = f"错误: 无法重命名 {filename} -> {new_name} ({str(e)})"
                errors.append(error_msg)
                print(error_msg)
                skipped_count += 1
    
    print("\n" + "=" * 50)
    print("处理完成!")
    print(f"重命名文件数: {renamed_count}")
    print(f"跳过文件数: {skipped_count}")
    print(f"错误数: {len(errors)}")
    
    # 显示所有错误信息
    if errors:
        print("\n错误详情:")
        for error in errors:
            print(f"  - {error}")
    
    return renamed_count

def main():
    # 显示将要执行的操作
    print("\n文件名批量重命名工具")
    print("=" * 50)
    print(f"目标目录: {TARGET_DIRECTORY}")
    print(f"文件名前缀: '{FILE_PREFIX}'")
    print(f"文件名后缀: '{FILE_SUFFIX}'")
    print("=" * 50)
    
    # 检查目录是否存在
    if not os.path.isdir(TARGET_DIRECTORY):
        print(f"\n错误: 目录不存在 - {TARGET_DIRECTORY}")
        return
    
    # 确认操作
    if not SKIP_CONFIRMATION:
        response = input("\n确定要执行重命名操作吗? (y/n): ").strip().lower()
        if response != 'y':
            print("操作已取消")
            return
    
    # 执行重命名
    rename_files(TARGET_DIRECTORY, FILE_PREFIX, FILE_SUFFIX)

if __name__ == "__main__":
    main()