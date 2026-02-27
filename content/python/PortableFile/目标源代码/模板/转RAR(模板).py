"""
ZIP/7Z转RAR批量转换工具 - 便携版
功能：使用嵌入式7z和WinRAR将拖动的文件/文件夹中的ZIP和7Z文件转换为RAR格式
无需安装任何软件，所有功能内置在单一Python文件中
"""

import os
import sys
import subprocess
import tempfile
import shutil
import base64
from tqdm import tqdm

# ===================== 嵌入式二进制数据 =====================


# ======================================================

class PortableCompressionTools:
    """
    便携式压缩工具管理器
    负责从嵌入式二进制数据中提取和管理7z和WinRAR工具
    """
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="compression_tools_")
        self.extracted_files = {}
        self.is_initialized = False
        
    def extract_binary(self, binary_data, filename):
        """
        从二进制数据提取文件到临时目录
        """
        if not binary_data:
            return None
            
        file_path = os.path.join(self.temp_dir, filename)
        try:
            # 解码base64数据
            clean_base64 = binary_data.replace('\n', '').replace(' ', '')
            file_data = base64.b64decode(clean_base64)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            return file_path
        except Exception as e:
            print(f"提取文件 {filename} 时出错: {str(e)}")
            return None
    
    def initialize_tools(self):
        """
        初始化工具，提取所有必要的二进制文件
        """
        if self.is_initialized:
            return True
            
        print("初始化便携式压缩工具...")
        
        try:
            # 7z文件映射
            sevenzip_files = [
                ("7z.exe", BIN_7Z),
                ("7z.dll", BIN_7Z_DLL),
                ("7z.sfx", BIN_7Z_SFX),
                ("7zCon.sfx", BIN_7ZCON_SFX),
            ]
            
            # WinRAR文件映射
            winrar_files = [
                ("WinRAR.exe", BIN_WINRAR),
                ("Rar.exe", BIN_RAR),
                ("UnRAR.exe", BIN_UNRAR),
                ("RarExt.dll", BIN_RAREXT_DLL),
            ]
            
            # 提取7z文件
            print("提取7z工具...")
            for filename, binary_data in sevenzip_files:
                if binary_data:
                    file_path = self.extract_binary(binary_data, filename)
                    if file_path:
                        self.extracted_files[filename] = file_path
                        print(f"  ✓ {filename}")
                    else:
                        print(f"  ✗ {filename} (提取失败)")
            
            # 提取WinRAR文件
            print("提取WinRAR工具...")
            for filename, binary_data in winrar_files:
                if binary_data:
                    file_path = self.extract_binary(binary_data, filename)
                    if file_path:
                        self.extracted_files[filename] = file_path
                        print(f"  ✓ {filename}")
                    else:
                        print(f"  ✗ {filename} (提取失败)")
            
            # 验证必要文件是否存在
            required_7z = ["7z.exe", "7z.dll"]
            required_winrar = ["WinRAR.exe", "RarExt.dll"]
            
            for req_file in required_7z:
                if req_file not in self.extracted_files:
                    print(f"错误: 缺少必要7z文件 - {req_file}")
                    return False
            
            for req_file in required_winrar:
                if req_file not in self.extracted_files:
                    print(f"错误: 缺少必要WinRAR文件 - {req_file}")
                    return False
            
            self.is_initialized = True
            print("✓ 工具初始化完成")
            return True
            
        except Exception as e:
            print(f"✗ 工具初始化失败: {str(e)}")
            return False
    
    def get_7z_path(self):
        """获取7z.exe路径"""
        return self.extracted_files.get("7z.exe")
    
    def get_winrar_path(self):
        """获取WinRAR.exe路径"""
        return self.extracted_files.get("WinRAR.exe")
    
    def get_rar_path(self):
        """获取Rar.exe路径（命令行版本）"""
        return self.extracted_files.get("Rar.exe")
    
    def cleanup(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"已清理临时目录: {self.temp_dir}")
        except Exception as e:
            print(f"清理临时文件时出错: {str(e)}")

def create_silent_process_config():
    """创建静默运行配置（适用于Windows系统）"""
    startupinfo = None
    creationflags = 0
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW
    return startupinfo, creationflags

def convert_zip_to_rar(zip_file, rar_file, tools_manager):
    """
    执行ZIP转RAR转换操作
    使用嵌入式WinRAR工具
    """
    startupinfo, creationflags = create_silent_process_config()
    temp_dir = tempfile.mkdtemp()
    
    winrar_path = tools_manager.get_winrar_path()
    if not winrar_path:
        return False, "WinRAR工具未找到"

    try:
        # 阶段1：解压ZIP文件到临时目录
        subprocess.run(
            [winrar_path, "x", "-ibck", "-idq", "-o+", zip_file, f"{temp_dir}\\"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=creationflags
        )

        # 阶段2：压缩为RAR文件
        subprocess.run(
            [winrar_path, "a", "-idq", "-ibck", "-ep1", "-r", "-o+", rar_file, f"{temp_dir}\\*.*"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=creationflags
        )

        return True, ""
    except subprocess.CalledProcessError as e:
        return False, f"子进程执行错误: {e.returncode}"
    except Exception as e:
        return False, f"意外错误: {str(e)}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def convert_7z_to_rar(seven_zip_file, rar_file, tools_manager):
    """
    执行7z转RAR转换操作
    使用嵌入式7z和WinRAR工具
    """
    startupinfo, creationflags = create_silent_process_config()
    
    sevenzip_path = tools_manager.get_7z_path()
    winrar_path = tools_manager.get_winrar_path()
    
    if not sevenzip_path:
        return False, "7z工具未找到"
    if not winrar_path:
        return False, "WinRAR工具未找到"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 阶段1：解压7z文件到临时目录
            subprocess.run(
                [sevenzip_path, "x", f"-o{temp_dir}", seven_zip_file, "-y", "-spd"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags
            )

            # 阶段2：压缩为RAR文件
            subprocess.run(
                [winrar_path, "a", "-idq", "-ibck", "-r", "-o+", "-ep1", rar_file, os.path.join(temp_dir, "*")],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            return True, ""
    except subprocess.CalledProcessError as e:
        return False, f"子进程执行错误: {str(e)}"
    except Exception as e:
        return False, f"意外错误: {str(e)}"

def process_file(file_path, tools_manager):
    """
    处理单个文件
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return False, f"文件不存在: {file_path}"
    
    # 获取文件扩展名
    ext = os.path.splitext(file_path)[1].lower()
    
    # 生成对应的RAR文件名
    rar_path = os.path.splitext(file_path)[0] + '.rar'
    
    # 如果RAR文件已存在，则跳过
    if os.path.exists(rar_path):
        return True, f"跳过: RAR文件已存在 - {os.path.basename(rar_path)}"
    
    # 根据文件类型调用相应的转换函数
    try:
        if ext == '.zip':
            success, message = convert_zip_to_rar(file_path, rar_path, tools_manager)
            if success:
                return True, f"成功: {os.path.basename(file_path)} -> {os.path.basename(rar_path)}"
            else:
                return False, f"转换失败: {os.path.basename(file_path)} - {message}"
        elif ext == '.7z':
            success, message = convert_7z_to_rar(file_path, rar_path, tools_manager)
            if success:
                return True, f"成功: {os.path.basename(file_path)} -> {os.path.basename(rar_path)}"
            else:
                return False, f"转换失败: {os.path.basename(file_path)} - {message}"
        else:
            return False, f"跳过: 不支持的文件类型 - {os.path.basename(file_path)}"
    except Exception as e:
        return False, f"异常: 处理文件时出错 - {os.path.basename(file_path)} - {str(e)}"

def process_directory(directory):
    """
    处理目录中的所有ZIP和7Z文件
    返回找到的文件列表
    """
    zip_files = []
    try:
        # 检查目录是否存在
        if not os.path.exists(directory):
            print(f"错误: 目录不存在 - {directory}")
            return zip_files
        
        # 遍历目录中的所有ZIP和7Z文件
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.zip', '.7z')):
                    full_path = os.path.join(root, file)
                    if os.path.isfile(full_path):
                        zip_files.append(full_path)
        
        return zip_files
    except Exception as e:
        print(f"异常: 处理目录时出错 - {directory} - {str(e)}")
        return zip_files

def main():
    """主函数"""
    tools_manager = None
    
    try:
        # 初始化便携式工具
        tools_manager = PortableCompressionTools()
        if not tools_manager.initialize_tools():
            print("错误: 无法初始化压缩工具")
            print("请确保二进制变量已正确填充")
            input("按任意键退出...")
            return
        
        # 处理命令行参数
        if len(sys.argv) > 1:
            # 收集所有需要处理的文件
            all_files = []
            
            # 处理每个参数
            for i in range(1, len(sys.argv)):
                target_path = sys.argv[i]
                print(f"扫描: {target_path}")
                
                if os.path.isfile(target_path):
                    # 如果是文件，直接添加到处理列表
                    all_files.append(target_path)
                elif os.path.isdir(target_path):
                    # 如果是目录，扫描目录中的所有ZIP和7Z文件
                    dir_files = process_directory(target_path)
                    all_files.extend(dir_files)
                else:
                    print(f"错误: 路径不存在 - {target_path}")
            
            # 去重
            all_files = list(set(all_files))
            
            if not all_files:
                print("未找到需要处理的ZIP或7Z文件")
                return
            
            print(f"找到 {len(all_files)} 个需要处理的文件")
            
            # 使用进度条处理每个文件
            success_count = 0
            with tqdm(all_files, desc="转换进度", unit="file", colour="blue") as pbar:
                for file_path in pbar:
                    base_name = os.path.basename(file_path)
                    pbar.set_postfix(file=base_name[:20])  # 显示前20个字符
                    
                    # 处理文件
                    success, message = process_file(file_path, tools_manager)
                    
                    # 处理结果
                    if success:
                        if "成功" in message:
                            success_count += 1
                        pbar.write(f"[✓] {message}")
                    else:
                        pbar.write(f"[✕] {message}")
            
            # 输出统计信息
            print(f"\n处理完成！成功转换 {success_count}/{len(all_files)} 个文件")
        else:
            print("请将文件或文件夹拖放到此程序上运行")
            print("\n使用方法:")
            print("1. 将ZIP或7Z文件/文件夹拖放到此程序图标上")
            print("2. 程序将自动转换为RAR格式")
            print("3. 如果同名的RAR文件已存在，将跳过转换")
            
    except Exception as e:
        print(f"程序异常: {str(e)}")
    finally:
        # 清理临时文件
        if tools_manager:
            tools_manager.cleanup()

if __name__ == "__main__":
    main()
    print("\n程序执行完毕，按任意键退出...")
    input()