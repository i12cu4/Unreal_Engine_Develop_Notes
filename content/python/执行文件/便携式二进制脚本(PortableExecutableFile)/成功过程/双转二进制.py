"""
压缩工具二进制导出工具
功能：将7z和WinRAR的所有必要文件转换为二进制变量，导出到单一文件
输出文件只包含变量定义，无其他代码
"""

import os
import base64

def binary_to_python_variable(file_path, variable_name):
    """
    将二进制文件转换为Python变量定义
    """
    try:
        with open(file_path, 'rb') as f:
            binary_data = f.read()
        
        # 转换为base64
        base64_data = base64.b64encode(binary_data).decode('utf-8')
        
        # 格式化为Python变量
        chunks = [base64_data[i:i+80] for i in range(0, len(base64_data), 80)]
        variable_definition = f'{variable_name} = """\\\n'
        variable_definition += '\\\n'.join(chunks)
        variable_definition += '"""\n\n'
        
        return variable_definition, len(binary_data)
    
    except Exception as e:
        print(f"错误处理文件 {file_path}: {str(e)}")
        return None, 0

def export_compression_tools_binary(sevenzip_dir, winrar_dir, output_file):
    """
    导出7z和WinRAR的二进制变量到单一文件
    """
    # 7z必要文件
    sevenzip_files = [
        ('7z.exe', 'BIN_7Z'),
        ('7z.dll', 'BIN_7Z_DLL'),
        ('7z.sfx', 'BIN_7Z_SFX'),
        ('7zCon.sfx', 'BIN_7ZCON_SFX'),
    ]
    
    # WinRAR必要文件
    winrar_files = [
        ('WinRAR.exe', 'BIN_WINRAR'),
        ('Rar.exe', 'BIN_RAR'),
        ('UnRAR.exe', 'BIN_UNRAR'),
        ('RarExt.dll', 'BIN_RAREXT_DLL'),
    ]
    
    print("开始导出压缩工具二进制文件...")
    print("=" * 50)
    
    # 生成只包含变量定义的Python文件
    python_code = "# 7z和WinRAR二进制数据变量定义\n# 此文件仅包含二进制数据变量，无其他代码\n\n"
    
    total_size = 0
    successful_files = 0
    
    # 处理7z文件
    print("处理7z文件:")
    for filename, var_name in sevenzip_files:
        file_path = os.path.join(sevenzip_dir, filename)
        if os.path.exists(file_path):
            print(f"  {filename}...", end=" ")
            variable_def, file_size = binary_to_python_variable(file_path, var_name)
            if variable_def:
                python_code += variable_def
                total_size += file_size
                successful_files += 1
                print(f"✓ ({file_size} 字节)")
            else:
                print("✗")
        else:
            print(f"  {filename}...✗ (文件不存在)")
    
    # 处理WinRAR文件
    print("\n处理WinRAR文件:")
    for filename, var_name in winrar_files:
        file_path = os.path.join(winrar_dir, filename)
        if os.path.exists(file_path):
            print(f"  {filename}...", end=" ")
            variable_def, file_size = binary_to_python_variable(file_path, var_name)
            if variable_def:
                python_code += variable_def
                total_size += file_size
                successful_files += 1
                print(f"✓ ({file_size} 字节)")
            else:
                print("✗")
        else:
            print(f"  {filename}...✗ (文件不存在)")
    
    # 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        print("\n" + "=" * 50)
        print(f"导出完成!")
        print(f"输出文件: {output_file}")
        print(f"成功处理: {successful_files} 个文件")
        print(f"总数据量: {total_size} 字节 ({total_size / 1024 / 1024:.2f} MB)")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"错误: 无法写入输出文件: {str(e)}")
        return False

if __name__ == "__main__":
    # ===================== 用户配置区域 =====================
    # 请修改以下三个变量来指定路径和输出文件名
    
    # 7z文件夹路径
    SEVENZIP_DIRECTORY = r"C:\Program File\7-Zip"  # 修改为您的7z文件夹路径
    
    # WinRAR文件夹路径
    WINRAR_DIRECTORY = r"C:\Program File\WinRAR"  # 修改为您的WinRAR文件夹路径
    
    # 输出文件名
    OUTPUT_FILENAME = "compression_tools_binary.py"  # 修改为您想要的输出文件名
    # ======================================================
    
    print("压缩工具二进制导出工具")
    print("=" * 50)
    print(f"7z源目录: {SEVENZIP_DIRECTORY}")
    print(f"WinRAR源目录: {WINRAR_DIRECTORY}")
    print(f"输出文件: {OUTPUT_FILENAME}")
    print("=" * 50)
    
    # 检查目录是否存在
    if not os.path.exists(SEVENZIP_DIRECTORY):
        print(f"错误: 指定的7z目录不存在 - {SEVENZIP_DIRECTORY}")
        input("按任意键退出...")
        exit(1)
    
    if not os.path.exists(WINRAR_DIRECTORY):
        print(f"错误: 指定的WinRAR目录不存在 - {WINRAR_DIRECTORY}")
        input("按任意键退出...")
        exit(1)
    
    # 执行导出
    success = export_compression_tools_binary(SEVENZIP_DIRECTORY, WINRAR_DIRECTORY, OUTPUT_FILENAME)
    
    if success:
        print("\n操作成功完成!")
        print(f"请将 {OUTPUT_FILENAME} 文件中的变量定义复制到您的主程序中")
    else:
        print("\n操作失败，请检查上述错误信息")
    
    input("按任意键退出...")