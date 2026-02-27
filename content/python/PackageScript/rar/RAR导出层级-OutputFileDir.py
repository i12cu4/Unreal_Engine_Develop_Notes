"""
RAR压缩包层级关系导出脚本
功能:
1. 提取RAR压缩包中的文件列表
2. 将文件列表转换为树形结构
3. 将树形结构保存(覆盖)为文本文件
4. 修复编码的解码问题(能够导出中文)
"""
import os
import subprocess

# ===================== 用户配置区域 =====================
target_dir = r"E:\Download"
rar_exe_path = r"C:\Program File\WinRAR\Rar.exe"
# ======================================================
def build_file_tree(file_list):
    """
    将文件列表转换为树形结构
    """
    # 创建根节点
    root = {}
    
    for file_path in file_list:
        parts = file_path.strip().replace('\\', '/').split('/')
        if not parts or not parts[0]:
            continue
            
        current = root
        # 遍历路径的每个部分
        for i, part in enumerate(parts):
            if part not in current:
                # 标记是否是文件（路径的最后一部分）
                current[part] = {'is_file': i == len(parts) - 1, 'children': {}}
            current = current[part]['children']
    
    return root

def tree_to_string(tree, indent=0, prefix=''):
    """
    将树形结构转换为字符串表示
    """
    if not tree:
        return ""
    
    result = []
    # 对节点按名称排序
    sorted_keys = sorted(tree.keys())
    
    for i, key in enumerate(sorted_keys):
        node = tree[key]
        # 判断是否是最后一个节点
        is_last = i == len(sorted_keys) - 1
        
        # 添加前缀符号
        connector = "└── " if is_last else "├── "
        result.append(f"{prefix}{connector}{key}")
        
        # 为子节点准备新的前缀
        child_prefix = prefix + ("    " if is_last else "│   ")
        
        # 递归处理子节点
        if node['children']:
            result.append(tree_to_string(node['children'], indent + 1, child_prefix))
    
    return "\n".join(result)

def process_rar_file(rar_path, txt_path, rar_exe_path):
    """
    处理单个RAR文件：提取内容并保存为树形结构的文本
    """
    # 如果txt文件已存在则删除
    if os.path.exists(txt_path):
        try:
            os.remove(txt_path)
            print(f"已删除旧文件: {os.path.basename(txt_path)}")
        except Exception as e:
            print(f"删除旧文件失败: {os.path.basename(txt_path)}, 错误: {e}")
            return False
    
    # 构建RAR命令
    command = [
        rar_exe_path,
        'lb',    # 使用简单列表模式（仅文件名）
        '-c-',   # 禁用注释显示
        rar_path
    ]
    
    # 执行命令并捕获输出
    try:
        print(f"正在处理: {os.path.basename(rar_path)}")
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # 检查执行结果
        if result.returncode != 0:
            error_msg = result.stderr.decode('gbk', errors='ignore').strip()
            print(f"处理失败: {os.path.basename(rar_path)}, 错误: {error_msg}")
            return False
        
        # 尝试多种编码解码输出
        encodings = ['utf-8', 'gbk', 'latin-1']
        output = None
        for encoding in encodings:
            try:
                output = result.stdout.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if output is None:
            print(f"无法解码输出: {os.path.basename(rar_path)}")
            return False
        
        # 分割文件列表并过滤空行
        file_list = [line for line in output.splitlines() if line.strip()]
        
        # 构建文件树
        file_tree = build_file_tree(file_list)
        
        # 转换为树形字符串
        tree_str = tree_to_string(file_tree)
        
        # 添加头部信息
        header = f"文件树结构: {os.path.basename(rar_path)}\n"
        header += "=" * 60 + "\n\n"
        footer = "\n\n" + "=" * 60 + f"\n文件总数: {len(file_list)}"
        
        full_content = header + (tree_str if tree_str else "（空压缩包）") + footer
        
        # 写入文本文件
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"已创建层级文件: {os.path.basename(txt_path)}")
        return True
        
    except Exception as e:
        print(f"处理过程中出错: {os.path.basename(rar_path)}, 错误: {str(e)}")
        return False

def extract_rar_structures(target_dir, rar_exe_path):
    """
    处理目标目录中的所有RAR文件
    """
    # 验证WinRAR可执行文件是否存在
    if not os.path.isfile(rar_exe_path):
        print(f"错误: 未找到WinRAR可执行文件: {rar_exe_path}")
        return False
    
    # 验证目标目录是否存在
    if not os.path.isdir(target_dir):
        print(f"错误: 目标目录不存在: {target_dir}")
        return False
    
    # 统计处理结果
    total = 0
    success = 0
    
    # 遍历目标目录中的所有文件
    for filename in os.listdir(target_dir):
        if filename.lower().endswith('.rar'):
            total += 1
            rar_path = os.path.join(target_dir, filename)
            
            # 生成对应的txt文件名（与rar文件同名）
            txt_filename = os.path.splitext(filename)[0] + '.txt'
            txt_path = os.path.join(target_dir, txt_filename)
            
            # 处理RAR文件
            if process_rar_file(rar_path, txt_path, rar_exe_path):
                success += 1
    
    print(f"\n处理完成！成功: {success}/{total} 个文件")
    return success == total

if __name__ == "__main__":
    # 执行处理
    extract_rar_structures(target_dir, rar_exe_path)
