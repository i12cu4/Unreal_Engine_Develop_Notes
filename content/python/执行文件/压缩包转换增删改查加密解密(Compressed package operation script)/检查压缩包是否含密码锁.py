import os
import subprocess
import sys
import ctypes

SEVEN_ZIP_PATH = r"C:\Program File\7-Zip\7z.exe"

def hide_console_window():
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, 0)

def is_password_protected(file_path):
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
        
        # 检查是否有真正的密码保护
        if result.returncode != 0:
            # 确认是密码错误而不是其他错误
            password_errors = ['password', 'encrypted', 'enter password', 'wrong password', 'file is encrypted']
            other_errors = ['cannot find', 'not found', 'no such file', 'is not archive', 'cannot open file']
            
            if any(err in output for err in password_errors) and not any(err in output for err in other_errors):
                return True
            return False
        
        # 检查详细列表中的加密标志
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
        
    except:
        return False

def main():
    hide_console_window()
    
    if not os.path.exists(SEVEN_ZIP_PATH):
        sys.exit(1)
    
    if len(sys.argv) > 1:
        target_path = sys.argv[1].strip('"').strip("'")
    else:
        target_path = input("").strip('"').strip("'")
    
    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        sys.exit(1)
    
    for root, dirs, files in os.walk(target_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in ['.rar', '.zip', '.7z']:
                if is_password_protected(file_path):
                    print(file_path)

if __name__ == "__main__":
    main()