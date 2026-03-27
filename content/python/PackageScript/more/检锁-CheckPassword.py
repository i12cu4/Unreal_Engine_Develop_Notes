import os
import subprocess
import sys
import ctypes

# 7-Zip 路径，根据实际安装位置修改
SEVEN_ZIP_PATH = r"C:\Program File\7-Zip\7z.exe"

# 不再隐藏控制台窗口，方便查看输出
# def hide_console_window():
#     kernel32 = ctypes.WinDLL('kernel32')
#     user32 = ctypes.WinDLL('user32')
#     hWnd = kernel32.GetConsoleWindow()
#     if hWnd:
#         user32.ShowWindow(hWnd, 0)

def is_password_protected(file_path):
    """检测单个压缩文件是否有密码保护"""
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        
        result = subprocess.run(
            [SEVEN_ZIP_PATH, "l", "-slt", "-p", "-ba", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=startupinfo,
            creationflags=0x08000000,  # CREATE_NO_WINDOW
            shell=False,
            timeout=30
        )
        
        output = (result.stdout + result.stderr).lower()
        
        # 如果返回码非零，检查是否是密码相关错误
        if result.returncode != 0:
            password_errors = ['password', 'encrypted', 'enter password', 'wrong password', 'file is encrypted']
            other_errors = ['cannot find', 'not found', 'no such file', 'is not archive', 'cannot open file']
            if any(err in output for err in password_errors) and not any(err in output for err in other_errors):
                return True
            return False
        
        # 返回码为零，检查详细输出中的加密标志
        lines = result.stdout.splitlines()
        for line in lines:
            line_lower = line.lower()
            if 'encrypted =' in line_lower and ('+' in line_lower or 'yes' in line_lower):
                return True
            if 'attributes =' in line_lower and 'encrypted' in line_lower:
                return True
            if line.strip().startswith('*') and '*' in line[1:]:
                if not any(x in line_lower for x in ['files:', 'folders:', 'bytes:', 'total', '----']):
                    return True
        return False
        
    except Exception as e:
        # 可在此添加调试输出，如 print(f"检查 {file_path} 时出错: {e}")
        return False

def process_path(path, encrypted_files):
    """处理单个路径：如果是目录则递归，如果是压缩文件则直接检测"""
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.rar', '.zip', '.7z']:
                    if is_password_protected(file_path):
                        encrypted_files.append(file_path)
    elif os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.rar', '.zip', '.7z']:
            if is_password_protected(path):
                encrypted_files.append(path)
    # 其他情况（如路径不存在）忽略

def main():
    # 不再隐藏控制台窗口
    # hide_console_window()
    
    # 检查 7-Zip 是否存在
    if not os.path.exists(SEVEN_ZIP_PATH):
        print(f"错误：找不到 7-Zip，请确认安装路径是否正确：{SEVEN_ZIP_PATH}")
        input("\n按回车键退出...")
        sys.exit(1)
    
    encrypted_files = []  # 存储找到的加密文件路径
    
    # 如果有命令行参数（拖放的文件/目录）
    if len(sys.argv) > 1:
        print("正在检查拖放的文件/目录...")
        for arg in sys.argv[1:]:
            path = arg.strip('"').strip("'")
            if os.path.exists(path):
                process_path(path, encrypted_files)
            else:
                print(f"警告：路径不存在，已跳过：{path}")
    else:
        # 没有参数时，交互输入一个目录
        target_path = input("请输入目录路径: ").strip('"').strip("'")
        if os.path.exists(target_path) and os.path.isdir(target_path):
            print("正在扫描目录...")
            process_path(target_path, encrypted_files)
        else:
            print("错误：输入路径不存在或不是一个目录")
            input("\n按回车键退出...")
            sys.exit(1)
    
    # 输出结果
    if encrypted_files:
        print("\n发现以下受密码保护的压缩文件：")
        for file_path in encrypted_files:
            print(file_path)
    else:
        print("\n未找到受密码保护的压缩文件。")
    
    # 等待用户按键，防止窗口闪退
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()