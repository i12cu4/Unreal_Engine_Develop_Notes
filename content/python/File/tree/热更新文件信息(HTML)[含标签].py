from bs4 import BeautifulSoup
import os
import sys
import ctypes
import re
import html
from ctypes import wintypes
import datetime
import argparse



# 新增：标签提取正则表达式
TAG_PATTERN = re.compile(r'^\[(.*?)\]')

# Windows 系统簇大小缓存
cluster_cache = {}

def get_cluster_size_windows(path):
    """获取Windows系统中文件所在磁盘的簇大小"""
    drive = os.path.splitdrive(path)[0]
    if not drive:
        drive = os.path.abspath(path)[:2]
    if drive in cluster_cache:
        return cluster_cache[drive]
    
    # 定义Windows API函数
    GetDiskFreeSpaceW = ctypes.windll.kernel32.GetDiskFreeSpaceW
    GetDiskFreeSpaceW.argtypes = [
        wintypes.LPCWSTR,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
    ]
    GetDiskFreeSpaceW.restype = wintypes.BOOL

    # 准备参数
    sectors_per_cluster = wintypes.DWORD()
    bytes_per_sector = wintypes.DWORD()
    free_clusters = wintypes.DWORD()
    total_clusters = wintypes.DWORD()

    # 调用API
    if not GetDiskFreeSpaceW(
        drive,
        ctypes.byref(sectors_per_cluster),
        ctypes.byref(bytes_per_sector),
        ctypes.byref(free_clusters),
        ctypes.byref(total_clusters),
    ):
        raise ctypes.WinError()
    
    cluster_size = sectors_per_cluster.value * bytes_per_sector.value
    cluster_cache[drive] = cluster_size
    return cluster_size

def get_allocated_size(file_path):
    """获取文件实际磁盘占用空间"""
    if os.name == 'nt':
        # Windows系统计算方式
        file_size = os.path.getsize(file_path)
        cluster_size = get_cluster_size_windows(file_path)
        return ((file_size + cluster_size - 1) // cluster_size) * cluster_size
    else:
        # Unix系统计算方式 (Linux/MacOS)
        return os.stat(file_path).st_blocks * 512

def extract_tag(filename):
    """从文件名中提取标签"""
    match = TAG_PATTERN.search(filename)
    return match.group(1).strip() if match else ""

# 修改后的文件信息收集函数
def collect_file_info(root_dir):
    """收集目录下所有文件信息"""
    file_info_list = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            absolute_path = os.path.abspath(file_path)
            try:
                # 获取文件信息
                size_bytes = get_allocated_size(file_path)
                file_info = {
                    '文件名': filename,
                    '标签': extract_tag(filename),  # 新增标签字段
                    '绝对路径': absolute_path,
                    '占用空间(GB)': size_bytes / (1024 ** 3),
                    '占用空间(KB)': size_bytes / 1024,
                    '字节数': os.path.getsize(file_path)
                }
                file_info_list.append(file_info)
            except Exception as e:
                print(f"处理文件失败 {file_path}: {str(e)}")
    return file_info_list

def generate_html_table(data):
    """生成HTML格式的表格"""
    headers = ['文件名', '标签', '绝对路径', '占用空间(GB)', '占用空间(KB)', '字节数']
    
    # 创建HTML表格结构
    html_table = [
        '<table border="1" style="border-collapse: collapse; width: 100%; margin: 20px 0;">',
        '<thead><tr style="background-color: #f2f2f2;">'
    ]
    
    # 添加表头
    for header in headers:
        html_table.append(f'<th style="padding: 8px; border: 1px solid #ddd;">{header}</th>')
    html_table.append('</tr></thead><tbody>')
    
    # 添加表格数据行
    for item in sorted(data, key=lambda x: x['占用空间(KB)'], reverse=True):
        html_table.append('<tr>')
        
        # 转义所有内容并格式化
        row = [
            html.escape(item['文件名']),
            html.escape(item['标签']),
            html.escape(item['绝对路径']),
            f"{item['占用空间(GB)']:.2f}",
            f"{item['占用空间(KB)']:.2f}",
            f"{item['字节数']:,}"  # 添加千位分隔符
        ]
        
        # 添加每列数据
        for col in row:
            html_table.append(f'<td style="padding: 8px; border: 1px solid #ddd;">{col}</td>')
        
        html_table.append('</tr>')
    
    html_table.append('</tbody></table>')
    return '\n'.join(html_table)

# 新增HTML解析函数（修复版）
def parse_existing_html(html_path):
    """解析已有HTML文件并提取结构化数据"""
    existing_data = []
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        table = soup.find('table')
        if not table or not table.thead:
            return existing_data

        # 获取标准化的表头映射
        headers = [th.text.strip() for th in table.thead.find_all('th')]
        header_map = {
            '文件名': '文件名',
            '标签': '标签',
            '绝对路径': '绝对路径',
            '占用空间(GB)': '占用空间(GB)',
            '占用空间(KB)': '占用空间(KB)',
            '字节数': '字节数'
        }

        # 处理表格正文
        for row in table.tbody.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) != len(headers):
                continue
            
            item = {}
            for i, raw_header in enumerate(headers):
                header = header_map.get(raw_header, raw_header)
                cell_text = cells[i].get_text(strip=True)
                
                # 类型转换处理
                if header == '占用空间(GB)':
                    item[header] = float(cell_text)
                elif header == '占用空间(KB)':
                    item[header] = float(cell_text)
                elif header == '字节数':
                    item[header] = int(cell_text.replace(',', ''))
                else:
                    # 处理HTML转义字符
                    item[header] = html.unescape(cell_text)
            
            # 标准化绝对路径
            if '绝对路径' in item:
                item['绝对路径'] = os.path.normpath(item['绝对路径'])
            existing_data.append(item)
            
    except Exception as e:
        print(f"解析现有文件异常: {str(e)}")
    
    return existing_data

# 修改后的主函数（增加去重选项）
def main(scan_path, html_path, deduplicate=True):
    """主函数，支持可配置的增量更新"""
    # 收集新数据并标准化路径
    new_data = []
    for item in collect_file_info(scan_path):
        item['绝对路径'] = os.path.normpath(item['绝对路径'])
        new_data.append(item)
    
    # 合并现有数据
    if os.path.exists(html_path):
        existing_data = parse_existing_html(html_path)
        
        if deduplicate:
            # 创建路径索引（不区分大小写）
            existing_paths = {os.path.normcase(item['绝对路径']) 
                            for item in existing_data}
            
            # 过滤已存在路径
            filtered_new = [
                item for item in new_data
                if os.path.normcase(item['绝对路径']) not in existing_paths
            ]
            combined_data = existing_data + filtered_new
        else:
            combined_data = existing_data + new_data
    else:
        combined_data = new_data
    
    # 生成并保存新报告
    table_content = generate_html_table(combined_data)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>文件空间分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        table {{ width: 100%; }}
        th {{ background-color: #3498db; color: white; }}
    </style>
</head>
<body>
    <h1>文件空间使用分析报告</h1>
    {table_content}
    <div style="margin-top: 20px; color: #7f8c8d; font-size: 0.9em;">
        生成时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
</body>
</html>"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    scan_path = r"E:\Download\UE资源整合包\道具"
    html_path = r"E:\Download\UE资源整合包\data6.html" 
    
    main(scan_path, html_path,True)#读取路径,输出路径,是否去重
    print("已生成HTML格式的文件分析报告")