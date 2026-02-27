import os
import re
from datetime import datetime

# 在这里设置您的HTML文件目录路径
HTML_FILES_DIRECTORY = r"C:\Users\chru\Downloads\托卡马克之冠\01答案备份\更早的答案"  # 请替换为实际路径

def extract_date_from_html(content):
    """从HTML内容中提取发布日期（优先使用data-tooltip属性）"""
    # 优先匹配data-tooltip属性中的发布时间（格式：发布于 2022-05-04 12:45）
    tooltip_pattern = re.compile(r'<span\s+data-tooltip="(发布于\s*\d{4}-\d{1,2}-\d{1,2}\s*\d{1,2}:\d{1,2})"')
    tooltip_match = tooltip_pattern.search(content)
    
    if tooltip_match:
        return tooltip_match.group(1).replace("发布于", "").strip()
    
    # 其次匹配meta标签中的创建时间
    meta_pattern = re.compile(r'<meta\s+itemprop="dateCreated"\s+content="(\d{4}-\d{2}-\d{2})T')
    meta_match = meta_pattern.search(content)
    
    if meta_match:
        return meta_match.group(1)
    
    # 最后匹配可见文本中的编辑/发布时间
    fallback_pattern = re.compile(r'(?:编辑于|发布于)\s*(\d{4}-\d{1,2}-\d{1,2}\s*\d{1,2}:\d{1,2})')
    fallback_match = fallback_pattern.search(content)
    
    if fallback_match:
        return fallback_match.group(1)
    
    return None

def format_date(raw_date):
    """将日期格式化为 YYYY.M.D 形式"""
    try:
        # 提取日期部分（去除时间部分）
        date_only = re.sub(r'\s*\d{1,2}:\d{1,2}$', '', raw_date.strip())
        # 处理可能的空格
        clean_date = date_only.replace(' ', '')
        # 转换为日期对象
        date_obj = datetime.strptime(clean_date, '%Y-%m-%d')
        # 格式化为 "2022.5.4"（去除前导零）
        return f"{date_obj.year}.{date_obj.month}.{date_obj.day}"
    except ValueError:
        return None

def rename_html_files():
    """重命名目录中的所有HTML文件"""
    # 检查目录是否存在
    if not os.path.isdir(HTML_FILES_DIRECTORY):
        print(f"错误: 目录不存在 - {HTML_FILES_DIRECTORY}")
        return
    
    print(f"开始处理目录: {HTML_FILES_DIRECTORY}")
    
    # 统计处理结果
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for filename in os.listdir(HTML_FILES_DIRECTORY):
        if not filename.lower().endswith('.html'):
            skipped_count += 1
            continue
            
        filepath = os.path.join(HTML_FILES_DIRECTORY, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            error_count += 1
            print(f"✖ 读取文件失败: {filename} ({str(e)})")
            continue
        
        # 提取日期
        raw_date = extract_date_from_html(content)
        if not raw_date:
            skipped_count += 1
            print(f"⚠ 未找到日期信息: {filename}")
            continue
        
        # 格式化日期
        formatted_date = format_date(raw_date)
        if not formatted_date:
            error_count += 1
            print(f"⚠ 日期格式无效: {raw_date} in {filename}")
            continue
        
        # 构建新文件名
        new_filename = f"{filename}{formatted_date}"
        new_filepath = os.path.join(HTML_FILES_DIRECTORY, new_filename)
        
        # 避免覆盖现有文件
        if os.path.exists(new_filepath):
            skipped_count += 1
            print(f"⚠ 文件已存在，跳过: {new_filename}")
            continue
        
        # 重命名文件
        try:
            os.rename(filepath, new_filepath)
            processed_count += 1
            print(f"✔ 重命名成功: {filename} → {new_filename}")
            print(f"   提取日期: {raw_date} → 格式化: {formatted_date}")
        except Exception as e:
            error_count += 1
            print(f"✖ 重命名失败: {filename} ({str(e)})")
    
    # 打印处理摘要
    print("\n===== 处理完成 =====")
    print(f"总文件数: {processed_count + skipped_count + error_count}")
    print(f"成功重命名: {processed_count}")
    print(f"跳过处理: {skipped_count}")
    print(f"处理错误: {error_count}")

if __name__ == "__main__":
    # 只需在此处设置目录路径，然后运行脚本
    rename_html_files()