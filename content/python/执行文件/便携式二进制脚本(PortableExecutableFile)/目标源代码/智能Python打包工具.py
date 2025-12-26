"""
极简Python打包工具
功能：将拖放的Python文件打包成EXE文件
使用方法：直接将.py文件拖放到此脚本上
"""

import os
import sys
import subprocess
import tempfile
import shutil

def main():
    print("=" * 50)
    print("极简Python打包工具")
    print("=" * 50)
    
    # 检查是否拖放了文件
    if len(sys.argv) < 2:
        print("使用方法：将.py文件拖放到此程序上")
        print("或者：python pack.py <your_script.py>")
        input("\n按回车键退出...")
        return
    
    # 获取要打包的文件
    python_file = sys.argv[1]
    
    if not os.path.exists(python_file):
        print(f"错误：文件不存在 - {python_file}")
        input("按回车键退出...")
        return
    
    if not python_file.lower().endswith('.py'):
        print("错误：请拖放Python文件 (.py)")
        input("按回车键退出...")
        return
    
    # 获取文件信息
    file_dir = os.path.dirname(python_file)
    file_name = os.path.basename(python_file)
    exe_name = os.path.splitext(file_name)[0] + '.exe'
    
    print(f"准备打包: {file_name}")
    print(f"输出文件: {exe_name}")
    print("-" * 50)
    
    # 检查PyInstaller是否安装
    try:
        subprocess.run(["pyinstaller", "--version"], 
                      capture_output=True, check=True)
        print("✓ PyInstaller已安装")
    except:
        print("未检测到PyInstaller，正在安装...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                          check=True)
            print("✓ PyInstaller安装成功")
        except Exception as e:
            print(f"✗ PyInstaller安装失败: {e}")
            input("按回车键退出...")
            return
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--onefile",           # 单个文件
        "--console",           # 控制台程序
        "--clean",             # 清理临时文件
        "--noconfirm",         # 覆盖而不确认
        "--distpath", file_dir,  # 输出到原文件目录
        f"--name={os.path.splitext(file_name)[0]}",
        python_file
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    print("正在打包，请稍候...")
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # 显示输出
        if result.stdout:
            print("\n标准输出:")
            print(result.stdout)
        
        if result.stderr:
            print("\n错误输出:")
            print(result.stderr)
        
        # 检查结果
        if result.returncode == 0:
            exe_path = os.path.join(file_dir, exe_name)
            if os.path.exists(exe_path):
                file_size = os.path.getsize(exe_path) / 1024 / 1024
                print("-" * 50)
                print(f"✓ 打包成功！")
                print(f"生成文件: {exe_path}")
                print(f"文件大小: {file_size:.2f} MB")
                
                # 清理临时文件
                spec_file = os.path.join(file_dir, file_name.replace('.py', '.spec'))
                build_dir = os.path.join(file_dir, "build")
                
                for item in [spec_file, build_dir]:
                    if os.path.exists(item):
                        try:
                            if os.path.isfile(item):
                                os.remove(item)
                            else:
                                shutil.rmtree(item)
                            print(f"已清理: {item}")
                        except:
                            pass
            else:
                print("✗ 打包失败：未生成EXE文件")
        else:
            print(f"✗ 打包失败，返回码: {result.returncode}")
    
    except subprocess.TimeoutExpired:
        print("✗ 打包超时（超过5分钟）")
    except Exception as e:
        print(f"✗ 打包过程中出错: {e}")
    
    print("\n" + "=" * 50)
    input("按回车键退出...")

if __name__ == "__main__":
    main()