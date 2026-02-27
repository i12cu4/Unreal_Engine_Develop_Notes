from bs4 import BeautifulSoup
import os
import argparse

def parse_and_colorize_html(input_file, output_file):
    """
    解析HTML文件并为不同盘符的路径着色
    :param input_file: 输入HTML文件路径
    :param output_file: 输出HTML文件路径
    """
    # 定义盘符颜色映射（可自定义修改）
    COLOR_MAPPING = {
        'C': '#FF0000',  # 红色
        'D': '#00FF00',  # 绿色
        'E': '#0000FF',  # 蓝色
        'F': '#FFA500',  # 橙色
        'G': '#800080',  # 紫色
        'H': '#FFC0CB'   # 粉色
    }
    
    # 默认样式（与原始样式保持一致）
    BASE_STYLE = "padding: 8px; border: 1px solid #ddd;"

    # 读取并解析HTML
    with open(input_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 定位表格和表头
    table = soup.find('table')
    if not table:
        raise ValueError("未找到有效表格")

    # 确定"绝对路径"列索引
    headers = table.thead.find_all('th')
    path_col_index = next(
        (i for i, h in enumerate(headers) if '绝对路径' in h.text),
        None
    )
    if path_col_index is None:
        raise ValueError("表格中缺少'绝对路径'列")

    # 遍历表格行
    for row in table.tbody.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) <= path_col_index:
            continue

        path_cell = cells[path_col_index]
        raw_path = path_cell.text.strip()
        
        # 提取盘符（兼容Windows路径）
        drive = os.path.splitdrive(raw_path)[0]
        if not drive:
            continue  # 跳过无效路径
            
        drive_letter = drive[0].upper()  # 获取盘符字母
        
        # 获取对应颜色
        color = COLOR_MAPPING.get(drive_letter, '#333333')  # 默认灰色
        
        # 保留原有样式并追加颜色
        existing_style = path_cell.get('style', '')
        new_style = f"{existing_style}; color: {color}; font-weight: bold;" 
        path_cell['style'] = new_style.strip('; ')

    # 保存修改后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"已生成带颜色样式的文件：{output_file}")

if __name__ == '__main__':
    """
    parser = argparse.ArgumentParser(description='HTML表格盘符着色工具')
    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('-o', '--output', default='output.html', 
                       help='输出文件路径（默认：output.html）')
    args = parser.parse_args()

    parse_and_colorize_html(args.input, args.output)
    """
    parse_and_colorize_html(r"E:\Download\UE资源整合包\data6.html", r"E:\Download\UE资源整合包\data7.html")
