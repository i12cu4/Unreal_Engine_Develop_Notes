"""
简易Python打包工具 - 修复版
功能：将拖放的Python文件打包成同名的EXE可执行文件
修复了Python 3.13与PyInstaller的兼容性问题
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
import threading

def is_frozen():
    """检查是否运行在打包后的EXE环境中"""
    return getattr(sys, 'frozen', False)

def check_pyinstaller():
    """检查是否安装了PyInstaller"""
    try:
        result = subprocess.run(["pyinstaller", "--version"], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def install_pyinstaller():
    """自动安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
        print("✓ PyInstaller安装成功")
        return True
    except Exception as e:
        print(f"✗ PyInstaller安装失败: {str(e)}")
        return False

def read_output(pipe, output_list, prefix=""):
    """读取子进程输出的线程函数"""
    try:
        with pipe:
            for line in iter(pipe.readline, ''):
                if line.strip():
                    output_line = f"{prefix}{line.strip()}"
                    print(output_line)
                    output_list.append(output_line)
    except Exception as e:
        print(f"读取输出时出错: {e}")

def package_to_exe(py_file_path):
    """将Python文件打包为EXE"""
    if not os.path.exists(py_file_path):
        print(f"错误: 文件不存在 - {py_file_path}")
        return False
    
    if not py_file_path.lower().endswith('.py'):
        print("错误: 请拖放Python文件 (.py)")
        return False
    
    # 获取文件信息
    file_dir = os.path.dirname(py_file_path)
    file_name = os.path.basename(py_file_path)
    exe_name = os.path.splitext(file_name)[0] + '.exe'
    # 将输出目录设置为与Python文件相同的目录
    output_dir = file_dir
    
    print(f"开始打包: {file_name}")
    print(f"输出目录: {output_dir}")
    print(f"输出文件: {exe_name}")
    print("-" * 50)
    
    # PyInstaller命令
    pyinstaller_cmd = [
        'pyinstaller',
        '--onefile',           # 单个文件
        '--console',           # 控制台程序
        '--clean',             # 清理临时文件
        '--noconfirm',         # 覆盖而不确认
        '--distpath', output_dir,  # 输出目录
        '--workpath', os.path.join(tempfile.gettempdir(), 'pyinstaller_build'),  # 构建目录放到临时文件夹
        '--name', os.path.splitext(file_name)[0],  # 输出文件名
        '--noupx',             # 禁用UPX压缩，提高兼容性
        py_file_path           # 要打包的Python文件
    ]
    
    try:
        print("正在打包，这可能需要几分钟...")
        print(f"执行命令: {' '.join(pyinstaller_cmd)}")
        start_time = time.time()
        
        # 创建临时目录用于构建
        os.makedirs(os.path.join(tempfile.gettempdir(), 'pyinstaller_build'), exist_ok=True)
        
        # 执行打包命令
        process = subprocess.Popen(
            pyinstaller_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=file_dir  # 在工作目录中执行
        )
        
        # 使用线程读取输出，避免阻塞
        stdout_lines = []
        stderr_lines = []
        
        stdout_thread = threading.Thread(
            target=read_output, 
            args=(process.stdout, stdout_lines)
        )
        stderr_thread = threading.Thread(
            target=read_output, 
            args=(process.stderr, stderr_lines, "ERROR: ")
        )
        
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        
        stdout_thread.start()
        stderr_thread.start()
        
        # 等待进程完成，带超时
        timeout = 600  # 10分钟超时
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            print(f"✗ 打包超时（超过{timeout}秒），终止进程...")
            process.terminate()
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                print("强制终止进程...")
                process.kill()
                process.wait()
            return False
        
        end_time = time.time()
        
        # 等待输出线程完成
        stdout_thread.join(timeout=5)
        stderr_thread.join(timeout=5)
        
        if returncode == 0:
            exe_path = os.path.join(output_dir, exe_name)
            if os.path.exists(exe_path):
                file_size = os.path.getsize(exe_path)
                print("-" * 50)
                print("✓ 打包成功!")
                print(f"生成文件: {exe_path}")
                print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
                print(f"耗时: {end_time - start_time:.2f} 秒")
                
                # 询问是否打开输出目录
                response = input("\n是否打开输出目录? (y/n): ").lower()
                if response == 'y':
                    try:
                        os.startfile(output_dir)
                    except:
                        print(f"无法打开目录: {output_dir}")
                
                return True
            else:
                print("✗ 打包失败: 未生成EXE文件")
                return False
        else:
            print(f"✗ 打包失败，返回码: {returncode}")
            if stderr_lines:
                print("\n错误信息:")
                for err_line in stderr_lines[-10:]:  # 显示最后10行错误
                    print(f"  {err_line}")
            return False
            
    except Exception as e:
        print(f"✗ 打包过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_temp_files(file_dir):
    """清理临时文件"""
    temp_items = [
        'build',
        '__pycache__',
        os.path.join(file_dir, 'build'),
        os.path.join(file_dir, '__pycache__')
    ]
    
    # 同时清理spec文件
    spec_files = [f for f in os.listdir(file_dir) if f.endswith('.spec')]
    for spec_file in spec_files:
        temp_items.append(os.path.join(file_dir, spec_file))
    
    cleaned_count = 0
    for item in temp_items:
        if os.path.exists(item):
            try:
                if os.path.isfile(item):
                    os.remove(item)
                else:
                    shutil.rmtree(item)
                print(f"已清理: {item}")
                cleaned_count += 1
            except Exception as e:
                print(f"清理失败 {item}: {str(e)}")
    
    return cleaned_count

def main():
    """主函数"""
    print("=" * 50)
    print("简易Python打包工具 - 修复版")
    print("修复了Python 3.13兼容性问题")
    if is_frozen():
        print("运行模式: 已打包的EXE程序")
    else:
        print("运行模式: Python脚本")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: 将.py文件拖放到此程序上")
        print("或者: python make_exe.py <python_file.py>")
        print("\n功能:")
        print("  - 自动检测并安装PyInstaller")
        print("  - 修复Python 3.13兼容性问题")
        print("  - 打包为单个EXE文件")
        print("  - 保持原文件名")
        print("  - 自动清理临时文件")
        input("\n按任意键退出...")
        return
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("未检测到PyInstaller")
        if not install_pyinstaller():
            print("请手动安装PyInstaller: pip install pyinstaller")
            input("按任意键退出...")
            return
    else:
        print("✓ PyInstaller已安装")
    
    # 处理每个拖放的文件
    success_count = 0
    for i in range(1, len(sys.argv)):
        py_file = sys.argv[i]
        file_dir = os.path.dirname(py_file)
        print(f"\n处理第 {i} 个文件: {os.path.basename(py_file)}")
        
        if package_to_exe(py_file):
            success_count += 1
        
        # 清理临时文件
        print("\n正在清理临时文件...")
        cleaned = cleanup_temp_files(file_dir)
        print(f"清理了 {cleaned} 个临时文件/目录")
    
    # 输出总结
    print("\n" + "=" * 50)
    if success_count > 0:
        print(f"✓ 成功打包 {success_count}/{len(sys.argv)-1} 个文件")
        print("\n使用说明:")
        print("1. 生成的EXE文件在源文件同目录下")
        print("2. 可以将EXE文件复制到任何Windows电脑使用")
        print("3. 无需安装Python或其他依赖")
    else:
        print("✗ 没有文件打包成功")
        print("\n可能的解决方案:")
        print("1. 确保Python文件没有语法错误")
        print("2. 尝试手动执行: pyinstaller --onefile your_script.py")
        print("3. 检查是否有特殊字符或空格在文件名中")
    print("=" * 50)
    
    input("按任意键退出...")

if __name__ == "__main__":
    main()