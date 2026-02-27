import os
import sys

def parse_existing_md(content):
    """解析Markdown文件中的表格数据"""
    lines = content.split('\n')
    table_data = {}
    header = []
    in_table = False

    for line in lines:
        if line.startswith('|') and '绝对路径' in line and '文件名' in line:
            header = [col.strip() for col in line.split('|')[1:-1]]
            in_table = True
            continue
        
        if in_table and line.startswith('|') and '---' in line:
            continue
        
        if in_table and line.startswith('|'):
            cols = [col.strip() for col in line.split('|')[1:-1]]
            if len(cols) != len(header):
                continue
            row = dict(zip(header, cols))
            try:
                # 转换数据类型
                row['标签'] = str(row['标签'])
                row['占用空间(GB)'] = float(row['占用空间(GB)'])
                row['占用空间(KB)'] = float(row['占用空间(KB)'])
                row['字节数'] = int(row['字节数'])
                table_data[row['绝对路径']] = row
            except (ValueError, KeyError):
                continue
        
        if in_table and not line.startswith('|'):
            break

    return table_data

def generate_merged_table(data):
    """生成合并后的Markdown表格"""
    headers = ['文件名','标签', '绝对路径', '占用空间(GB)', '占用空间(KB)', '字节数']
    table = ['| ' + ' | '.join(headers) + ' |']
    table.append('|-' + '-|-'.join(['-'*len(h) for h in headers]) + '-|')
    
    # 按字节数降序排序
    sorted_data = sorted(data.values(), key=lambda x: x['字节数'], reverse=True)
    
    for item in sorted_data:
        row = [
            item['文件名'],
            item['标签'],
            item['绝对路径'],
            f"{item['占用空间(GB)']:.6f}",
            f"{item['占用空间(KB)']:.2f}",
            str(item['字节数'])
        ]
        table.append('| ' + ' | '.join(row) + ' |')
    
    return '\n'.join(table)

def merge_markdown_files(output_path, input_paths):
    """合并多个Markdown文件"""
    merged_data = {}
    
    # 遍历所有输入文件
    for input_path in input_paths:
        if not os.path.exists(input_path):
            print(f"警告：跳过不存在的文件 {input_path}")
            continue
            
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 合并数据（后出现的文件覆盖先前数据）
        merged_data.update(parse_existing_md(content))
    
    # 生成新表格
    final_table = generate_merged_table(merged_data)
    
    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_table)

if __name__ == '__main__':
    """
    if len(sys.argv) < 3:
        print("使用方法: python merge_md.py <输出文件> <输入文件1> [输入文件2 ...]")
        print("示例: python merge_md.py merged.md file1.md file2.md")
        sys.exit(1)
    """
    
    output_path = r"G:\c3.md"
    input_paths = [r"G:\c1.md", r"G:\c2.md"]
    
    merge_markdown_files(output_path, input_paths)
    print(f"已合并 {len(input_paths)} 个文件到 {output_path}")
