"""
WinRAR二进制导出工具
功能：将WinRAR完整功能块转换为Python变量形式的二进制数据
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
        # 将长字符串分割为多行，每行80字符
        chunks = [base64_data[i:i+80] for i in range(0, len(base64_data), 80)]
        variable_definition = f'{variable_name} = """\\\n'
        variable_definition += '\\\n'.join(chunks)
        variable_definition += '"""'
        
        return variable_definition, len(binary_data)
    
    except Exception as e:
        print(f"错误处理文件 {file_path}: {str(e)}")
        return None, 0

def create_winrar_binary_module(winrar_dir, output_file):
    """
    创建包含WinRAR完整功能块的Python模块
    """
    # WinRAR完整功能所需的文件
    essential_files = [
        'WinRAR.exe',           # 主程序
        'Rar.exe',              # 命令行版本
        'UnRAR.exe',            # 解压工具
        'RarExt.dll',           # 扩展DLL
        'Rar.txt',              # 许可文件
        'Order.txt',            # 订单信息
    ]
    
    # 可选的文件（如果有的话也包含）
    optional_files = [
        'WinRAR32.exe',         # 32位版本
        'Rar32.exe',            # 32位命令行
        'UnRAR32.exe',          # 32位解压工具
        'RarFiles.lst',         # 文件列表
        'WhatsNew.txt',         # 更新说明
        'License.txt',          # 许可协议
    ]
    
    print("开始导出WinRAR二进制文件...")
    print("=" * 50)
    
    # 收集所有存在的文件
    all_files = []
    for filename in essential_files + optional_files:
        file_path = os.path.join(winrar_dir, filename)
        if os.path.exists(file_path):
            all_files.append((filename, file_path))
            print(f"找到: {filename}")
    
    if not all_files:
        print("错误: 未找到任何WinRAR文件")
        return False
    
    # 生成Python代码
    python_code = '''"""
WinRAR完整功能二进制数据模块
包含WinRAR便携版的完整二进制数据
生成的Python变量可以直接在代码中使用
"""

import base64
import os
import tempfile
import subprocess
import sys

'''
    
    total_size = 0
    successful_files = 0
    
    for filename, file_path in all_files:
        print(f"处理: {filename}...", end=" ")
        
        # 生成变量名（去掉扩展名，添加前缀）
        var_name = f"BIN_{os.path.splitext(filename)[0].replace('-', '_').upper()}"
        
        variable_def, file_size = binary_to_python_variable(file_path, var_name)
        
        if variable_def:
            python_code += variable_def + "\n\n"
            total_size += file_size
            successful_files += 1
            print(f"✓ ({file_size} 字节)")
        else:
            print("✗")
    
    # 添加工具函数
    python_code += '''
def get_winrar_binary(variable_name):
    """
    从base64字符串获取二进制数据
    """
    base64_str = globals().get(variable_name)
    if not base64_str:
        raise ValueError(f"未找到变量: {variable_name}")
    
    # 移除换行符和空格
    clean_base64 = base64_str.replace('\\n', '').replace(' ', '')
    return base64.b64decode(clean_base64)

def extract_winrar_file(filename, binary_variable, target_dir=None):
    """
    提取单个WinRAR文件到目标目录
    """
    if target_dir is None:
        target_dir = tempfile.mkdtemp(prefix="winrar_extract_")
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    file_path = os.path.join(target_dir, filename)
    binary_data = get_winrar_binary(binary_variable)
    
    with open(file_path, 'wb') as f:
        f.write(binary_data)
    
    return file_path

def extract_all_winrar_files(target_dir=None):
    """
    提取所有WinRAR文件到目标目录
    返回包含文件路径的字典
    """
    if target_dir is None:
        target_dir = tempfile.mkdtemp(prefix="winrar_complete_")
    
    extracted_files = {}
    
    # 尝试提取主要文件
    files_to_extract = [
        ('WinRAR.exe', 'BIN_WINRAR'),
        ('Rar.exe', 'BIN_RAR'),
        ('UnRAR.exe', 'BIN_UNRAR'),
        ('RarExt.dll', 'BIN_RAREXT_DLL'),
    ]
    
    for filename, var_name in files_to_extract:
        try:
            file_path = extract_winrar_file(filename, var_name, target_dir)
            extracted_files[filename] = file_path
            print(f"提取: {filename}")
        except Exception as e:
            print(f"警告: 无法提取 {filename}: {str(e)}")
    
    return extracted_files, target_dir

def get_winrar_exe_path(target_dir=None):
    """
    获取WinRAR.exe的完整路径
    如果不存在则自动提取
    """
    extracted_files, extract_dir = extract_all_winrar_files(target_dir)
    return extracted_files.get('WinRAR.exe')

def get_rar_exe_path(target_dir=None):
    """
    获取Rar.exe的完整路径
    如果不存在则自动提取
    """
    extracted_files, extract_dir = extract_all_winrar_files(target_dir)
    return extracted_files.get('Rar.exe')

# 模块信息
def get_module_info():
    """
    获取模块信息
    """
    info = {
        'name': 'WinRAR完整二进制模块',
        'files_embedded': %d,
        'total_size': %d,
        'description': '包含WinRAR便携版的完整功能二进制数据'
    }
    return info

if __name__ == "__main__":
    info = get_module_info()
    print("WinRAR二进制模块信息:")
    print(f"嵌入文件数量: {info['files_embedded']}")
    print(f"总大小: {info['total_size']} 字节 ({info['total_size'] / 1024 / 1024:.2f} MB)")
    print(f"描述: {info['description']}")
''' % (successful_files, total_size)
    
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
    # 请修改以下两个变量来指定WinRAR文件夹路径和输出文件名
    
    # WinRAR文件夹路径（包含WinRAR.exe等文件的目录）
    WINRAR_DIRECTORY = r"C:\Program File\WinRAR"  # 修改为您的WinRAR文件夹路径
    
    # 输出文件名
    OUTPUT_FILENAME = "winrar_binary_data.py"  # 修改为您想要的输出文件名
    # ======================================================
    
    print("WinRAR二进制导出工具")
    print("=" * 50)
    print(f"WinRAR源目录: {WINRAR_DIRECTORY}")
    print(f"输出文件: {OUTPUT_FILENAME}")
    print("=" * 50)
    
    # 检查WinRAR目录是否存在
    if not os.path.exists(WINRAR_DIRECTORY):
        print(f"错误: 指定的WinRAR目录不存在 - {WINRAR_DIRECTORY}")
        print("请检查 WINRAR_DIRECTORY 变量是否正确设置")
        input("按任意键退出...")
        exit(1)
    
    # 执行导出
    success = create_winrar_binary_module(WINRAR_DIRECTORY, OUTPUT_FILENAME)
    
    if success:
        print("\n操作成功完成!")
    else:
        print("\n操作失败，请检查上述错误信息")
    
    input("按任意键退出...")