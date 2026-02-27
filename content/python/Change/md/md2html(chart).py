import re
import html
import sys

def md_table_to_html(md_text):
    """
    将Markdown表格文本转换为HTML表格
    """
    lines = md_text.strip().split('\n')
    if not lines:
        return ""
    
    # 提取表头 - 处理可能的前导管道符
    headers = [cell.strip() for cell in lines[0].strip('|').split('|') if cell.strip()]
    
    # 提取表格数据行（跳过分隔线）
    data_rows = []
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # 跳过空行和分隔线
        if i == 0:  # 跳过表头行（已处理）
            continue
        if not stripped_line:  # 跳过空行
            continue
        if re.match(r'^[\|:?\s-]+$', stripped_line):  # 跳过分隔线
            continue
            
        # 处理可能的前导/尾随管道符
        cells = [cell.strip() for cell in stripped_line.strip('|').split('|')]
        
        # 保留空单元格（显示为空白）
        if any(cell.strip() for cell in cells):  # 检查行是否包含任何非空内容
            data_rows.append(cells)
    
    # 构建HTML表格
    if not headers and not data_rows:
        return ""  # 空表格不渲染
    
    html_table = ['<table>']
    
    # 添加表头（如果有）
    if headers:
        html_table.append('  <thead>')
        html_table.append('    <tr>')
        for header in headers:
            html_table.append(f'      <th>{html.escape(header)}</th>')
        html_table.append('    </tr>')
        html_table.append('  </thead>')
    
    # 添加表格数据（如果有）
    if data_rows:
        html_table.append('  <tbody>')
        for row in data_rows:
            html_table.append('    <tr>')
            for cell in row:
                # 保留空单元格（显示为空白）
                html_table.append(f'      <td>{html.escape(cell)}</td>')
            html_table.append('    </tr>')
        html_table.append('  </tbody>')
    
    html_table.append('</table>')
    return '\n'.join(html_table)

def convert_md_file_to_html(input_file, output_file):
    """
    转换Markdown文件中的表格为HTML文件
    """
    try:
        # 读取Markdown文件内容为行列表
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        tables = []  # 存储每个表格的文本
        current_table = []  # 当前正在处理的表格行
        in_table = False   # 是否在表格中
        table_state = 0     # 0: 未开始, 1: 表头已读, 2: 分隔线已读

        for line in lines:
            stripped_line = line.strip()
            has_pipe = '|' in stripped_line
            
            # 检查是否是分隔线
            is_separator = re.match(r'^[\|\s:-]+$', stripped_line) if stripped_line else False
            
            # 状态机处理表格
            if not in_table:
                if has_pipe and not is_separator:
                    # 可能是表头行
                    current_table = [stripped_line]
                    in_table = True
                    table_state = 1
            else:
                if table_state == 1:  # 表头已读，需要分隔线
                    if is_separator:
                        current_table.append(stripped_line)
                        table_state = 2
                    elif has_pipe:
                        # 可能是没有分隔线的表格，直接接受为数据行
                        current_table.append(stripped_line)
                        table_state = 2  # 跳过分隔线检查
                    else:
                        # 不符合表格格式，重置
                        current_table = []
                        in_table = False
                        table_state = 0
                elif table_state == 2:  # 分隔线已读（或无分隔线），处理数据行
                    if has_pipe or is_separator or not stripped_line:
                        # 保留空行和分隔线（在表格转换函数中会过滤）
                        current_table.append(stripped_line)
                    else:
                        # 非表格内容，结束当前表格
                        tables.append('\n'.join(current_table))
                        current_table = []
                        in_table = False
                        table_state = 0  # 修复：重置状态为0
            
            # 如果当前不在表格中，但遇到分隔线，可能是格式错误的表格
            if not in_table and is_separator:
                current_table = []
                in_table = False
                table_state = 0
        
        # 处理文件末尾的表格
        if in_table and current_table:
            tables.append('\n'.join(current_table))
        
        if not tables:
            print("警告: 未检测到任何Markdown表格")
            tables = []  # 确保空列表
        
        # 转换所有表格（包括可能为空的表格）
        html_tables = []
        for i, table in enumerate(tables):
            html_table = md_table_to_html(table)
            if html_table:  # 只添加非空表格
                html_tables.append(html_table)
            else:
                print(f"警告: 跳过空表格 #{i+1}")
        
        # 生成完整HTML文档
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Markdown表格转换结果</title>
    <style>
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
            font-family: Arial, sans-serif;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left; 
            min-width: 80px;
        }}
        th {{ 
            background-color: #4CAF50; 
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
        }}
        tr:nth-child(even) {{ 
            background-color: #f8f8f8; 
        }}
        tr:hover {{ 
            background-color: #f1f8e9; 
        }}
        .empty-cell {{
            background-color: #f5f5f5;
        }}
        hr {{ 
            margin: 40px 0; 
            border: 0; 
            border-top: 2px dashed #4CAF50; 
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2E7D32;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.2rem;
        }}
        .info {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-style: italic;
        }}
        .no-tables {{
            text-align: center;
            padding: 40px;
            border: 1px dashed #ccc;
            border-radius: 5px;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Markdown表格转换结果</h1>
        <div class="info">共检测到 {len(tables)} 个表格，成功转换 {len(html_tables)} 个</div>
        
        {"<hr>".join(html_tables) if html_tables else """
        <div class="no-tables">
            <h2>未发现有效表格</h2>
            <p>输入的Markdown文件中未检测到符合格式的表格</p>
            <p>请确保表格使用标准的Markdown格式：</p>
            <pre>
| 表头1 | 表头2 |
|-------|-------|
| 内容1 | 内容2 |
| 内容3 | 内容4 |</pre>
        </div>
        """}
    </div>
    
    <script>
        // 自动为表格中的空单元格添加特殊样式
        document.addEventListener('DOMContentLoaded', function() {{
            const tables = document.querySelectorAll('table');
            tables.forEach(table => {{
                const rows = table.querySelectorAll('tr');
                rows.forEach(row => {{
                    const cells = row.querySelectorAll('td, th');
                    cells.forEach(cell => {{
                        if (!cell.textContent.trim()) {{
                            cell.classList.add('empty-cell');
                            cell.innerHTML = '&nbsp;'; // 确保空单元格有高度
                        }}
                    }});`
                }});
            }});
        }});
    </script>
</body>
</html>"""
        
        # 写入HTML文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"转换成功！已生成HTML文件: {output_file}")
        print(f"检测到 {len(tables)} 个表格，成功转换 {len(html_tables)} 个")
        if len(tables) > len(html_tables):
            print(f"警告: 跳过了 {len(tables) - len(html_tables)} 个空表格")
    
    except Exception as e:
        print(f"转换出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    input_file = r"C:\Users\Administrator\Desktop\live-notes\data\badline.md"
    output_file = r"C:\Users\Administrator\Desktop\live-notes\data\badline.html"
    convert_md_file_to_html(input_file, output_file)

