import re
import os
import html2text
from bs4 import BeautifulSoup
import quopri
import email
import chardet
import datetime

def process_mht_files(input_path, output_folder=None):
    """处理单个或批量MHT文件转换"""
    if os.path.isfile(input_path) and input_path.lower().endswith('.mht'):
        return [convert_mht_to_txt(input_path, output_folder)]
    
    if os.path.isdir(input_path):
        converted_files = []
        for filename in os.listdir(input_path):
            if filename.lower().endswith('.mht'):
                filepath = os.path.join(input_path, filename)
                try:
                    result = convert_mht_to_txt(filepath, output_folder)
                    if result:  # 仅添加成功转换的结果
                        converted_files.append(result)
                except Exception as e:
                    print(f"转换失败 {filename}: {str(e)}")
        return converted_files
    
    raise ValueError("无效的输入路径")

def convert_mht_to_txt(input_file, output_folder=None):
    """转换单个MHT文件并返回处理信息"""
    # 读取MHT文件内容
    with open(input_file, 'rb') as f:
        content = f.read()
    
    # 提取HTML内容
    html_content = extract_html_from_mht(content)
    if html_content is None:
        raise ValueError("未找到有效的HTML内容")
    
    # 使用BeautifulSoup解析
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除不需要的元素
    for element in soup(['script', 'style', 'noscript', 'meta', 'link', 
                        'button', 'footer', 'header', 'aside', 'nav',
                        'svg', 'figure', 'form', 'iframe', 'input',
                        'img', 'video', 'audio', 'object', 'embed']):
        element.decompose()
    
    # 转换为文本
    text_content = convert_html_to_text(str(soup))
    
    # 步骤1: 提取标题（第一行有效内容） - 在删除操作之前进行
    title = extract_title(text_content)
    
    # 步骤2: 清理内容：删除"谢邀"行及之前的内容
    cleaned_text = remove_before_thankyou(text_content)
    
    # 步骤3: 提取日期并清理"发布于"/"编辑于"行及之后的内容
    date_prefix, cleaned_text = extract_date_and_clean(cleaned_text)
    
    # 生成文件名
    filename = generate_filename(title, date_prefix)
    
    # 确定输出路径
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, filename)
    else:
        output_path = os.path.join(os.path.dirname(input_file), filename)
    
    # 处理重名文件
    counter = 1
    original_output_path = output_path
    while os.path.exists(output_path):
        name, ext = os.path.splitext(original_output_path)
        output_path = f"{name}_{counter}{ext}"
        counter += 1
    
    # 保存清理后的文本
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    
    return {
        'input_file': input_file,
        'output_file': output_path,
        'title': title,
        'date': date_prefix
    }

def extract_html_from_mht(content):
    """从MHT文件中提取HTML内容"""
    try:
        # 方法1: 使用email标准库解析
        msg = email.message_from_bytes(content)
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                payload = part.get_payload(decode=True)
                try:
                    return payload.decode('utf-8')
                except:
                    detected = chardet.detect(payload)
                    return payload.decode(detected['encoding'] or 'utf-8', 'ignore')
    except:
        pass
    
    # 方法2: 手动解析
    try:
        for boundary in [b'boundary="', b'BOUNDARY="', b'boundary=', b'BOUNDARY=']:
            start = content.find(boundary)
            if start != -1:
                start += len(boundary)
                end = content.find(b'"', start)
                if end == -1:
                    end = content.find(b'\n', start)
                if end != -1:
                    boundary_str = content[start:end].strip(b'"')
                    parts = content.split(b'--' + boundary_str)
                    for part in parts:
                        if b'text/html' in part:
                            html_part = re.split(b'\n\s*\n', part, maxsplit=1)[-1]
                            if b'quoted-printable' in part:
                                return quopri.decodestring(html_part).decode('utf-8', 'ignore')
                            else:
                                detected = chardet.detect(html_part)
                                return html_part.decode(detected['encoding'] or 'utf-8', 'ignore')
    except:
        pass
    
    # 方法3: 直接搜索HTML标签
    try:
        html_start = content.find(b'<html')
        if html_start == -1:
            html_start = content.find(b'<!DOCTYPE')
        if html_start != -1:
            html_end = content.find(b'</html>', html_start)
            if html_end != -1:
                html_part = content[html_start:html_end + 7]
                detected = chardet.detect(html_part)
                return html_part.decode(detected['encoding'] or 'utf-8', 'ignore')
    except:
        pass
    
    return None

def convert_html_to_text(html):
    """将HTML转换为格式化的纯文本"""
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_emphasis = True
    h.body_width = 0
    h.single_line_break = False
    
    # 处理知乎特定格式
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'</p>', '</p>\n\n', html)
    
    return h.handle(html)

def extract_title(text_content):
    """提取第一行有效内容作为标题（在删除操作之前）"""
    lines = text_content.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped:
            # 清理标题格式：移除方括号和URL部分
            clean_title = clean_title_format(stripped)
            # 移除特殊字符（Windows文件名限制）
            clean_title = re.sub(r'[\\/*?:"<>|]', '', clean_title)
            # 移除知乎常见前缀
            clean_title = re.sub(r'^#+\s*', '', clean_title)  # 移除Markdown标题符号
            return clean_title[:100]  # 限制长度
    return "知乎回答"

def clean_title_format(title):
    """清理标题中的Markdown链接格式"""
    # 处理类似: [标题](https://...)
    match = re.match(r'^\[(.*?)\]\(https?://.*\)$', title)
    if match:
        return match.group(1)
    
    # 处理类似: [标题]
    match = re.match(r'^\[(.*?)\]$', title)
    if match:
        return match.group(1)
    
    # 处理标题结尾的URL
    title = re.sub(r'\s*https?://\S+$', '', title)
    
    return title

def remove_before_thankyou(text_content):
    """删除'谢邀'行及之前的所有内容"""
    lines = text_content.splitlines()
    found_index = -1
    
    # 查找最后一个包含"谢邀"的行
    for i, line in enumerate(lines):
        if "谢邀" in line:
            found_index = i
    
    # 如果找到，保留该行之后的内容
    if found_index >= 0:
        return "\n".join(lines[found_index+1:])
    
    return text_content

def extract_date_and_clean(text_content):
    """提取日期并清理相关内容"""
    # 查找日期模式
    date_match = re.search(r'(发布于|编辑于)\s*(\d{4})-(\d{1,2})-(\d{1,2})', text_content)
    date_prefix = ""
    
    if date_match:
        # 提取并格式化日期 (YYYY.M.D)
        year, month, day = date_match.group(2), date_match.group(3), date_match.group(4)
        date_prefix = f"{year}.{int(month)}.{int(day)}"
        
        # 删除所有包含"发布于"或"编辑于"的行及其之后的内容
        lines = text_content.splitlines()
        for i, line in enumerate(lines):
            if "发布于" in line or "编辑于" in line:
                cleaned_text = "\n".join(lines[:i])
                # 清理多余空行
                cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text.strip())
                return date_prefix, cleaned_text
    
    # 如果没有找到日期行，返回原始内容（已清理）
    cleaned_text = re.sub(r'\n{3,}', '\n\n', text_content.strip())
    return date_prefix, cleaned_text

def generate_filename(title, date_prefix):
    """生成规范化的文件名"""
    # 如果标题为空，使用默认标题
    if not title.strip():
        title = "知乎回答"
    
    # 如果日期为空，尝试使用当前日期
    if not date_prefix:
        today = datetime.datetime.now()
        date_prefix = f"{today.year}.{today.month}.{today.day}"
    
    # 生成文件名
    filename = f"{date_prefix} {title}.txt"
    
    # 确保文件名长度合理
    if len(filename) > 150:
        filename = filename[:150] + ".txt"
    
    return filename

def print_conversion_report(results):
    """打印转换结果报告"""
    if not results:
        print("没有成功转换的文件")
        return
    
    print("\n转换报告:")
    print("=" * 60)
    print(f"{'输入文件':<30}{'输出文件':<40}{'标题/日期'}")
    print("-" * 60)
    
    for result in results:
        input_name = os.path.basename(result['input_file'])[:25]
        output_name = os.path.basename(result['output_file'])[:35]
        title_date = f"{result['title']}" + (f" ({result['date']})" if result['date'] else "")
        
        print(f"{input_name:<30}{output_name:<40}{title_date[:30]}")
    
    print("=" * 60)
    print(f"成功转换 {len(results)} 个文件")

if __name__ == "__main__":
    print("知乎MHT转TXT工具 v3.1")
    print("=" * 60)
    print("功能说明:")
    print("- 批量转换指定路径下的所有MHT文件")
    print("- 先提取标题，再删除'谢邀'行及之前的内容")
    print("- 清理标题中的方括号和URL")
    print("- 删除包含'发布于'/'编辑于'的行及之后的内容")
    print("- 提取日期作为文件名前缀 (格式: YYYY.M.D)")
    print("=" * 60)
    
    input_path = r"C:\Users\chru\Desktop\123"
    output_folder = input_path
    if not output_folder:
        output_folder = None
    
    try:
        results = process_mht_files(input_path, output_folder)
        if results:
            print_conversion_report(results)
        else:
            print("未找到可转换的MHT文件")
    except Exception as e:
        print(f"处理失败: {str(e)}")
