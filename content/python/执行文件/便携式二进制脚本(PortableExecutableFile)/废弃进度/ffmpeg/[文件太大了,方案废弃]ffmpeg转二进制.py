import os
import base64

def file_to_binary_variable(file_path, variable_name):
    """将文件转换为二进制变量"""
    with open(file_path, 'rb') as f:
        binary_data = f.read()
    
    # 转换为base64编码的字符串
    base64_data = base64.b64encode(binary_data).decode('utf-8')
    
    return f"{variable_name} = b'{base64_data}'\n"

def main():
    # 配置FFmpeg文件夹路径
    ffmpeg_folder = r"C:\Program File\ffmpeg\bin"
    
    # 输出Python文件路径 - 当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_py_file = os.path.join(current_dir, "ffmpeg_binary_data.py")
    
    # 需要处理的FFmpeg文件
    ffmpeg_files = {
        'ffmpeg_exe_binary': 'ffmpeg.exe',
        'ffprobe_exe_binary': 'ffprobe.exe'
    }
    
    # 生成Python文件内容
    py_content = "# FFmpeg二进制数据 - 自动生成\n# 不要手动修改此文件\n\n"
    
    # 处理每个文件
    for var_name, file_name in ffmpeg_files.items():
        file_path = os.path.join(ffmpeg_folder, file_name)
        
        if os.path.exists(file_path):
            print(f"正在处理: {file_name}")
            py_content += file_to_binary_variable(file_path, var_name)
            py_content += "\n"
        else:
            print(f"警告: 文件未找到 - {file_path}")
    
    # 写入Python文件
    with open(output_py_file, 'w', encoding='utf-8') as f:
        f.write(py_content)
    
    print(f"FFmpeg二进制数据已保存到: {output_py_file}")
    print(f"生成的变量: {list(ffmpeg_files.keys())}")

if __name__ == "__main__":
    main()