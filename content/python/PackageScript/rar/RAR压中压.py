import os
import sys
import subprocess
import shutil

# 配置WinRAR路径
WINRAR_PATH = r"C:\Program File\WinRAR\Rar.exe"

# 配置目标移动路径（如果需要移动文件，填写有效路径；留空或无效路径则不移动）
TARGET_MOVE_PATH = ""  # 例如: r"D:\NestedCompressedArchives"

def validate_winrar():
    """验证WinRAR是否存在"""
    if not os.path.exists(WINRAR_PATH):
        print(f"错误: WinRAR未找到在 {WINRAR_PATH}")
        return False
    return True

def validate_target_path():
    """验证目标移动路径是否有效"""
    if not TARGET_MOVE_PATH:
        return False
    
    if not os.path.exists(TARGET_MOVE_PATH):
        print(f"注意: 目标移动路径不存在: {TARGET_MOVE_PATH}")
        return False
    
    if not os.path.isdir(TARGET_MOVE_PATH):
        print(f"注意: 目标移动路径不是文件夹: {TARGET_MOVE_PATH}")
        return False
    
    return True

def collect_input_paths():
    """收集通过拖放传入的文件/文件夹路径"""
    if len(sys.argv) < 2:
        print("请拖放一个或多个文件/文件夹到此脚本上")
        input("按Enter键退出...")
        sys.exit(1)
    
    # 获取除脚本自身外的所有参数
    return [os.path.abspath(path) for path in sys.argv[1:]]

def find_all_rar_files(paths):
    """递归查找所有RAR文件"""
    rar_files = []
    
    for path in paths:
        if os.path.isfile(path) and path.lower().endswith('.rar'):
            rar_files.append(os.path.abspath(path))
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.lower().endswith('.rar'):
                        rar_files.append(os.path.abspath(os.path.join(root, file)))
    
    return rar_files

def list_rar_contents(rar_path):
    """使用WinRAR列出压缩包内所有文件名"""
    try:
        # 使用vb命令只输出文件名列表
        result = subprocess.run(
            [WINRAR_PATH, 'vb', rar_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            check=True
        )
        
        # 处理输出，移除空行
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        # 静默处理错误，不输出详细错误信息
        return []
    except Exception:
        return []

def contains_compressed_files(file_list):
    """检查文件列表是否包含7z/rar/zip文件"""
    compressed_extensions = ('.7z', '.rar', '.zip')
    return any(file.lower().endswith(compressed_extensions) for file in file_list)

def move_detected_files(detected_rars):
    """移动检测到的RAR文件到目标路径"""
    if not validate_target_path():
        print("\n跳过移动操作：目标路径无效或未设置")
        return False
    
    print(f"\n开始移动 {len(detected_rars)} 个文件到: {TARGET_MOVE_PATH}")
    successful_moves = 0
    failed_moves = 0
    
    for rar_path in detected_rars:
        filename = os.path.basename(rar_path)
        destination = os.path.join(TARGET_MOVE_PATH, filename)
        
        # 检查目标文件是否已存在
        if os.path.exists(destination):
            print(f"跳过 {filename}：目标位置已存在同名文件")
            failed_moves += 1
            continue
        
        try:
            shutil.move(rar_path, destination)
            print(f"已移动: {filename}")
            successful_moves += 1
        except Exception as e:
            print(f"移动失败 {filename}: {str(e)}")
            failed_moves += 1
    
    print(f"\n移动操作完成: 成功 {successful_moves} 个, 失败 {failed_moves} 个")
    return successful_moves > 0

def main():
    # 验证WinRAR
    if not validate_winrar():
        input("按Enter键退出...")
        sys.exit(1)
    
    # 收集输入路径
    input_paths = collect_input_paths()
    
    # 查找所有RAR文件
    rar_files = find_all_rar_files(input_paths)
    
    if not rar_files:
        print("未找到任何RAR文件。")
        input("按Enter键退出...")
        sys.exit(0)
    
    print(f"找到 {len(rar_files)} 个RAR文件，正在检查内容...")
    
    # 检查每个RAR文件
    detected_rars = []
    for rar_file in rar_files:
        files = list_rar_contents(rar_file)
        if files and contains_compressed_files(files):
            detected_rars.append(rar_file)
    
    # 输出结果
    if detected_rars:
        print("\n发现以下RAR文件中包含其他压缩文件:")
        for rar_path in detected_rars:
            print(rar_path)
        
        # 如果设置了有效的目标路径，则移动文件
        if TARGET_MOVE_PATH:
            move_detected_files(detected_rars)
    else:
        print("\n未发现包含其他压缩文件的RAR文件。")
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main()
