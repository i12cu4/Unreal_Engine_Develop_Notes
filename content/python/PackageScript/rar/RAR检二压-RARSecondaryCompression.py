"""
RAR压缩包搜寻二次压缩(启用rar指令)
功能: 扫描指定目录下的所有RAR文件，并分析其内容，查找是否存在二次压缩包文件。
# 修复了中文显示的编码问题
# 完整输出了压缩包的信息
# 增加了对无效文件的警告提示
"""
import os
import subprocess

# ===================== 用户配置区域 =====================
TARGET_DIRECTORY = r"E:\Download"  # 扫描目标目录
WINRAR_PATH = r"C:\Program File\WinRAR\rar.exe"  # WinRAR执行路径
# ======================================================

def analyze_rar_contents(rar_path):
    """分析RAR文件内容，返回包含压缩文件的列表（文件名，类型）"""
    try:
        cmd = [WINRAR_PATH, 'lb', '-n', rar_path]
        
        # 修改编码处理方式
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=False  # 禁用自动解码
        )

        # 手动解码输出内容（Windows系统通常使用GBK编码）
        try:
            output = result.stdout.decode('gbk', errors='replace')
        except UnicodeDecodeError:
            output = result.stdout.decode('utf-8', errors='replace')
        
        compressed_files = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            
            # 直接处理解码后的字符串
            filename = os.path.basename(line)
            name, ext = os.path.splitext(filename)
            ext = ext.lower().lstrip('.')
            
            if ext in {'zip', '7z', 'rar'} and ext:
                compressed_files.append( (filename, ext) )
        
        return compressed_files
    
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('gbk', errors='replace') if e.stderr else "未知错误"
        print(f"\033[31m错误\033[0m 处理失败: {os.path.basename(rar_path)}\n原因: {error_msg.strip()}")
        return []
    except Exception as e:
        print(f"\033[31m意外错误\033[0m 处理: {rar_path}\n类型: {type(e).__name__}\n详情: {str(e)}")
        return []

def main():
    # 路径验证（保持不变）
    if not os.path.isfile(WINRAR_PATH):
        print(f"\033[31m致命错误\033[0m WinRAR不存在于: {WINRAR_PATH}")
        return
    
    if not os.path.exists(TARGET_DIRECTORY):
        print(f"\033[31m致命错误\033[0m 目标目录不存在: {TARGET_DIRECTORY}")
        return
    if not os.path.isdir(TARGET_DIRECTORY):
        print(f"\033[31m致命错误\033[0m 路径不是目录: {TARGET_DIRECTORY}")
        return

    # 文件处理逻辑（保持不变）
    for root, _, files in os.walk(TARGET_DIRECTORY):
        for file in files:
            if file.lower().endswith('.rar'):
                full_path = os.path.join(root, file)
                try:
                    if not os.path.isfile(full_path):
                        print(f"\033[33m警告\033[0m 跳过无效文件: {full_path}")
                        continue
                    
                    compressed_entries = analyze_rar_contents(full_path)
                    
                    if compressed_entries:
                        print(f"\n\033[32m发现压缩文件\033[0m: {full_path}")
                        print("包含以下压缩包:")
                        type_counter = {}
                        for filename, ext in compressed_entries:
                            type_counter.setdefault(ext, []).append(filename)
                        
                        for ext, files in type_counter.items():
                            print(f"  [{ext.upper()}] 类型 ({len(files)} 个):")
                            for f in files:
                                print(f"    - {f}")
                except Exception as e:
                    print(f"\033[31m处理中断\033[0m 文件: {full_path}\n错误类型: {type(e).__name__}")

if __name__ == "__main__":
    main()
