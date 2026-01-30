"""
UE版本检测工具
功能:
1. 读取RAR压缩包中的.uproject和.uplugin文件
2. 提取UE引擎版本信息
3. 在终端显示每个压缩包的UE版本
4. 无需安装WinRAR，使用嵌入式工具
5. 只读操作，不修改任何文件
"""

import os
import sys
import argparse
import json
import base64
import tempfile
import shutil
import subprocess
from pathlib import Path
from collections import namedtuple
from tqdm import tqdm

# ===================== 嵌入式二进制数据占位符 =====================
# 这些变量将在后期填充实际的Base64编码的二进制数据
BIN_RAR = ""       # Rar.exe 命令行工具
BIN_UNRAR = ""     # UnRAR.exe 解压工具
BIN_RAREXT_DLL = "" # RarExt.dll 支持库
# ======================================================

# 定义结果结构
UEResult = namedtuple('UEResult', ['rar_path', 'success', 'file_type', 'file_path', 'engine_version', 'error_msg'])

class PortableRARTools:
    """便携式RAR工具管理器，负责提取和管理嵌入式WinRAR工具"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="ue_rar_tools_")
        self.extracted_files = {}
        self.is_initialized = False
        self.rar_exe_path = None
        self.unrar_exe_path = None
        
    def extract_binary(self, binary_data, filename):
        """从二进制数据提取文件到临时目录"""
        if not binary_data or not binary_data.strip():
            print(f"警告: {filename} 的二进制数据为空")
            return None
            
        file_path = os.path.join(self.temp_dir, filename)
        try:
            # 清理Base64字符串中的空格和换行
            clean_base64 = binary_data.replace('\n', '').replace(' ', '').replace('\r', '')
            if not clean_base64:
                print(f"警告: {filename} 的Base64数据为空")
                return None
                
            file_data = base64.b64decode(clean_base64)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            # 确保文件具有执行权限(对非Windows系统)
            if os.name != 'nt':
                os.chmod(file_path, 0o755)
            return file_path
        except Exception as e:
            print(f"提取文件 {filename} 时出错: {str(e)}")
            return None
    
    def initialize_tools(self):
        """初始化工具，提取所有必要的二进制文件"""
        if self.is_initialized:
            return True
            
        print("初始化便携式RAR工具...")
        
        try:
            rar_files = [
                ("Rar.exe", BIN_RAR),
                ("UnRAR.exe", BIN_UNRAR),
                ("RarExt.dll", BIN_RAREXT_DLL),
            ]
            
            # 提取所有文件
            for filename, binary_data in rar_files:
                if binary_data:
                    file_path = self.extract_binary(binary_data, filename)
                    if file_path:
                        self.extracted_files[filename] = file_path
                        print(f"  ✓ {filename} -> {file_path}")
                    else:
                        print(f"  ✗ {filename} (提取失败)")
            
            # 设置工具路径
            self.rar_exe_path = self.extracted_files.get("Rar.exe")
            self.unrar_exe_path = self.extracted_files.get("UnRAR.exe")
            
            # 优先使用UnRAR.exe，如果不可用则使用Rar.exe
            if not self.unrar_exe_path and self.rar_exe_path:
                self.unrar_exe_path = self.rar_exe_path
                print("  注意: 使用Rar.exe代替UnRAR.exe")
            
            if not self.unrar_exe_path:
                print("错误: 无法获取解压工具路径")
                return False
            
            if not os.path.exists(self.unrar_exe_path):
                print(f"错误: 解压工具不存在: {self.unrar_exe_path}")
                return False
            
            self.is_initialized = True
            print(f"✓ RAR工具初始化完成 (路径: {self.unrar_exe_path})")
            return True
            
        except Exception as e:
            print(f"✗ RAR工具初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_unrar_exe_path(self):
        """获取解压工具路径"""
        return self.unrar_exe_path
    
    def cleanup(self):
        """清理临时文件"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"已清理临时目录: {self.temp_dir}")
        except Exception as e:
            print(f"清理临时文件时出错: {str(e)}")

def get_silent_args():
    """获取静默模式参数，隐藏子进程窗口"""
    if os.name == 'nt':
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0  # 隐藏窗口
        return {'startupinfo': si}
    return {}

def list_rar_contents(rar_path, unrar_exe_path):
    """列出RAR文件中的所有文件"""
    try:
        cmd = [unrar_exe_path, 'lb', rar_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, **get_silent_args())
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return files
    except subprocess.CalledProcessError as e:
        print(f"错误: 无法列出 {os.path.basename(rar_path)} 的内容: {str(e)}")
        return []
    except Exception as e:
        print(f"错误: 列出 {os.path.basename(rar_path)} 内容时发生异常: {str(e)}")
        return []

def extract_file_from_rar(rar_path, file_path_in_rar, output_path, unrar_exe_path):
    """从RAR文件中提取单个文件"""
    try:
        # 创建输出目录
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 构建命令 - 提取单个文件
        cmd = [unrar_exe_path, 'e', '-y', '-idq', rar_path, file_path_in_rar, os.path.dirname(output_path) + os.sep]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, **get_silent_args())
        
        # 检查输出文件是否存在
        if os.path.exists(output_path):
            return True
        else:
            print(f"警告: 文件提取成功但未找到: {output_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"错误: 无法提取 {file_path_in_rar} 从 {os.path.basename(rar_path)}: {str(e)}")
        print(f"  错误输出: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"错误: 提取 {file_path_in_rar} 时发生异常: {str(e)}")
        return False

def parse_uproject_file(file_path):
    """解析.uproject文件，提取引擎版本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 尝试获取EngineAssociation
        engine_version = data.get('EngineAssociation', '')
        if not engine_version:
            # 尝试其他可能的字段
            engine_version = data.get('EngineVersion', '')
            
        return engine_version.strip()
    except Exception as e:
        print(f"解析.uproject文件错误: {str(e)}")
        return ""

def parse_uplugin_file(file_path):
    """解析.uplugin文件，提取引擎版本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取EngineVersion
        engine_version = data.get('EngineVersion', '')
        return engine_version.strip()
    except Exception as e:
        print(f"解析.uplugin文件错误: {str(e)}")
        return ""

def detect_ue_version_in_rar(rar_path, unrar_exe_path, temp_dir):
    """在RAR文件中检测UE版本"""
    results = []
    
    # 1. 列出RAR中的所有文件
    files = list_rar_contents(rar_path, unrar_exe_path)
    if not files:
        return [UEResult(rar_path, False, "", "", "", "无法读取压缩包内容")]
    
    # 2. 筛选出.uoproject和.uplugin文件
    ue_files = []
    for file in files:
        if file.lower().endswith('.uproject') or file.lower().endswith('.uplugin'):
            ue_files.append(file)
    
    if not ue_files:
        return [UEResult(rar_path, False, "", "", "", "未找到.uproject或.uplugin文件")]
    
    # 3. 处理每个找到的UE文件
    for ue_file in ue_files:
        try:
            # 创建临时文件路径
            safe_filename = "".join(c for c in os.path.basename(ue_file) if c.isalnum() or c in ('.', '_')).rstrip()
            temp_file_path = os.path.join(temp_dir, safe_filename)
            
            # 4. 提取文件
            if not extract_file_from_rar(rar_path, ue_file, temp_file_path, unrar_exe_path):
                results.append(UEResult(rar_path, False, "", ue_file, "", "文件提取失败"))
                continue
            
            # 5. 根据文件类型解析
            file_type = ""
            engine_version = ""
            
            if ue_file.lower().endswith('.uproject'):
                file_type = "Project"
                engine_version = parse_uproject_file(temp_file_path)
            elif ue_file.lower().endswith('.uplugin'):
                file_type = "Plugin"
                engine_version = parse_uplugin_file(temp_file_path)
            
            # 6. 检查是否成功获取版本
            if not engine_version:
                results.append(UEResult(rar_path, False, file_type, ue_file, "", "无法解析引擎版本"))
            else:
                results.append(UEResult(rar_path, True, file_type, ue_file, engine_version, ""))
            
            # 7. 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
        except Exception as e:
            results.append(UEResult(rar_path, False, "", ue_file, "", f"处理错误: {str(e)}"))
    
    return results

def generate_report(results):
    """生成并打印结果报告"""
    print("\n" + "=" * 70)
    print("UE版本检测结果:")
    print("=" * 70)
    
    for res in results:
        status_icon = "✓" if res.success else "✗"
        file_info = f"[{res.file_type}]" if res.file_type else "[未知]"
        
        if res.success:
            print(f"{status_icon} {os.path.basename(res.rar_path)}")
            print(f"   文件: {res.file_path}")
            print(f"   类型: {file_info}")
            print(f"   UE版本: {res.engine_version}")
        else:
            print(f"{status_icon} {os.path.basename(res.rar_path)} - {res.error_msg}")
            if res.file_path:
                print(f"   相关文件: {res.file_path}")
    
    # 统计信息
    total_files = len(set([r.rar_path for r in results]))
    successful = len([r for r in results if r.success])
    print("\n" + "-" * 70)
    print(f"总计: {total_files} 个RAR文件, 成功分析: {successful} 个")

def collect_input_paths(paths):
    """收集输入路径，支持文件和文件夹"""
    input_files = []
    
    for path in paths:
        path_obj = Path(path)
        if not path_obj.exists():
            print(f"警告: 路径不存在 - {path}")
            continue
        
        if path_obj.is_file():
            if path_obj.suffix.lower() == '.rar':
                input_files.append(str(path_obj))
            else:
                print(f"跳过非RAR文件: {path_obj.name}")
        elif path_obj.is_dir():
            # 递归查找所有RAR文件
            rar_count = 0
            for rar_file in path_obj.rglob('*.rar'):
                input_files.append(str(rar_file))
                rar_count += 1
            print(f"在文件夹 '{path_obj.name}' 中找到 {rar_count} 个RAR文件")
    
    return input_files

def wait_for_exit():
    """等待用户按键退出"""
    if sys.platform.startswith('win'):
        print("\n程序执行完毕，按任意键退出...")
        try:
            import msvcrt
            msvcrt.getch()
        except:
            input()
    else:
        input("\n程序执行完毕，按回车键退出...")

def main():
    # 创建RAR工具管理器
    tools_manager = PortableRARTools()
    
    try:
        # 初始化工具
        if not tools_manager.initialize_tools():
            print("错误: 无法初始化RAR工具")
            print("请确保二进制变量已正确填充")
            wait_for_exit()
            return
        
        unrar_exe_path = tools_manager.get_unrar_exe_path()
        if not unrar_exe_path:
            print("错误: 无法获取解压工具路径")
            wait_for_exit()
            return
        
        print(f"使用解压工具: {unrar_exe_path}")
        
        # 解析命令行参数
        parser = argparse.ArgumentParser(description='检测RAR压缩包中的UE版本')
        parser.add_argument('paths', nargs='*', help='RAR文件或包含RAR文件的文件夹路径')
        args = parser.parse_args()
        
        # 获取输入路径
        input_paths = args.paths
        if not input_paths:
            print("提示: 您可以将RAR文件或文件夹拖放到此程序上，或直接输入路径")
            user_input = input("请拖放文件/文件夹或输入路径: ").strip().strip('"')
            if not user_input:
                print("未提供路径，程序退出")
                tools_manager.cleanup()
                wait_for_exit()
                return
            input_paths = [user_input]
        
        # 收集所有RAR文件
        rar_files = collect_input_paths(input_paths)
        
        if not rar_files:
            print("未找到任何RAR文件，程序退出")
            tools_manager.cleanup()
            wait_for_exit()
            return
        
        print(f"\n找到 {len(rar_files)} 个RAR文件:")
        for i, rar_file in enumerate(rar_files, 1):
            print(f"  {i:2d}. {os.path.basename(rar_file)}")
        
        # 确认处理
        input(f"\n按回车键开始分析这 {len(rar_files)} 个文件...")
        
        # 创建临时目录用于提取文件
        with tempfile.TemporaryDirectory(prefix="ue_temp_") as temp_dir:
            print(f"使用临时目录: {temp_dir}")
            
            # 处理每个RAR文件
            all_results = []
            print("\n开始分析RAR文件...")
            
            with tqdm(rar_files, desc="分析进度", unit="file") as pbar:
                for rar_path in pbar:
                    pbar.set_postfix(file=os.path.basename(rar_path)[:20])
                    
                    # 检查文件是否存在
                    if not os.path.exists(rar_path):
                        all_results.append(UEResult(rar_path, False, "", "", "", "文件不存在"))
                        continue
                    
                    # 分析RAR文件
                    results = detect_ue_version_in_rar(rar_path, unrar_exe_path, temp_dir)
                    all_results.extend(results)
            
            # 生成报告
            generate_report(all_results)
    
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理工具
        tools_manager.cleanup()
    
    # 等待退出
    wait_for_exit()

if __name__ == "__main__":
    main()