import os

def process_md_file(input_path, output_path):
    """
    处理Markdown文件：读取输入文件，解析层级结构，输出到新文件
    """
    try:
        # 读取输入文件
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 首先检测缩进类型（制表符还是空格）
        indent_type = None
        indent_size = 4  # 默认假设4个空格作为一个缩进级别
        
        for line in lines:
            if line.strip() and not line.startswith('\t') and line.startswith(' '):
                # 检测到空格缩进
                indent_type = 'spaces'
                # 计算缩进大小（找到第一个非空格字符的位置）
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    indent_size = leading_spaces
                break
            elif line.strip() and line.startswith('\t'):
                # 检测到制表符缩进
                indent_type = 'tabs'
                break
        
        print(f"检测到的缩进类型: {indent_type}, 缩进大小: {indent_size}")
        
        # 解析层级结构并转换为目录树格式
        output_lines = []
        # 用于跟踪每个层级的连接状态
        connection_status = {}
        
        for i, line in enumerate(lines):
            if not line.strip():
                # 空行直接保留
                output_lines.append(line)
                continue
                
            # 计算缩进级别
            indent_level = 0
            if indent_type == 'tabs':
                # 计算制表符数量
                for char in line:
                    if char == '\t':
                        indent_level += 1
                    else:
                        break
                content = line.lstrip('\t')
            else:
                # 计算空格缩进级别
                leading_spaces = len(line) - len(line.lstrip(' '))
                indent_level = leading_spaces // indent_size
                content = line[leading_spaces:]
            
            # 构建目录树前缀
            prefix = ""
            
            # 对于有缩进的行，添加目录树符号
            if indent_level > 0:
                # 检查后续行来确定当前行是否是父级的最后一个子节点
                is_last = True
                for j in range(i + 1, len(lines)):
                    if not lines[j].strip():
                        continue  # 跳过空行
                    
                    # 计算后续行的缩进级别
                    next_indent_level = 0
                    if indent_type == 'tabs':
                        for char in lines[j]:
                            if char == '\t':
                                next_indent_level += 1
                            else:
                                break
                    else:
                        next_leading_spaces = len(lines[j]) - len(lines[j].lstrip(' '))
                        next_indent_level = next_leading_spaces // indent_size
                    
                    # 如果找到同级或更高级别的行，则当前行不是最后一个
                    if next_indent_level < indent_level:
                        break
                    elif next_indent_level == indent_level:
                        is_last = False
                        break
                
                # 添加垂直连接线
                for lvl in range(indent_level - 1):
                    # 检查这个层级是否需要垂直连接线
                    if lvl in connection_status and connection_status[lvl]:
                        prefix += "│   "
                    else:
                        prefix += "    "
                
                # 添加当前节点的连接线
                if is_last:
                    prefix += "└── "
                    # 更新连接状态 - 这个层级的连接结束
                    connection_status[indent_level - 1] = False
                else:
                    prefix += "├── "
                    # 更新连接状态 - 这个层级需要继续连接
                    connection_status[indent_level - 1] = True
            
            # 添加目录树格式的行
            output_lines.append(prefix + content)
        
        # 写入输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
            
        print(f"成功处理文件！输出已保存到: {output_path}")
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        import traceback
        traceback.print_exc()
        
# 使用示例
if __name__ == "__main__":
    # 指定输入和输出文件路径
    input_md_path = r"C:\Users\chru\Desktop\Unreal_Engine_Develop_Notes\README2.md"  # 替换为你的输入文件路径
    output_md_path = r"C:\Users\chru\Desktop\Unreal_Engine_Develop_Notes\README3.md"  # 替换为你想要的输出文件路径
    
    # 处理文件
    process_md_file(input_md_path, output_md_path)