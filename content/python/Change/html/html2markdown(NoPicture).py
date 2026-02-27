import os
import re
import html2text
from pathlib import Path

def html_to_md(html_file_path, output_dir=None):
    """
    将单个HTML文件转换为Markdown格式并进行内容过滤
    :param html_file_path: HTML文件路径
    :param output_dir: 输出目录（默认同HTML文件目录）
    :return: 生成的Markdown文件路径
    """
    # 读取HTML内容
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 配置html2text转换器
    h = html2text.HTML2Text()
    h.ignore_links = False       # 保留链接（后续会处理）
    h.ignore_images = False      # 保留图片（后续会过滤特定图片）
    h.ignore_tables = False      # 保留表格
    h.bypass_tables = False
    h.mark_code = True           # 标记代码块
    h.body_width = 0             # 禁用换行
    h.single_line_break = True   # 单换行视为空格
    
    # 转换为Markdown
    md_content = h.handle(html_content)
    
    # ================= 内容过滤 =================
    # 1. 过滤空alt文本的图片标记：![](任意内容)
    md_content = re.sub(r'!\[\]\([^)]*\)', '', md_content)
    
    # 2. 将链接标记 [文本](URL) 替换为纯文本
    md_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', md_content)
    
    # 3. 过滤纯装饰性水平线（三个以上连字符）
    md_content = re.sub(r'\n-{3,}\n', '\n\n', md_content)
    
    # 4. 过滤空的方括号标记：[]
    md_content = re.sub(r'\[\]', '', md_content)
    
    # 5. 清理多余空行（三个以上换行变为两个）
    md_content = re.sub(r'\n{3,}', '\n\n', md_content)
    
    # 6. 删除行首尾的空白字符
    md_content = '\n'.join(line.strip() for line in md_content.split('\n'))
    
    # 7. 移除剩余的孤立方括号（可选）
    md_content = re.sub(r'\[([^\]]+)\]', r'\1', md_content)
    # ===========================================
    
    # 设置输出路径
    if output_dir is None:
        output_dir = os.path.dirname(html_file_path)
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    md_filename = Path(html_file_path).stem + '.md'
    md_path = os.path.join(output_dir, md_filename)
    
    # 保存Markdown文件
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return md_path

def batch_convert_html_to_md(input_dir, output_dir=None, extension='.html'):
    """
    批量转换目录中的HTML文件
    :param input_dir: 包含HTML文件的目录
    :param output_dir: 输出目录（默认同输入目录）
    :param extension: 要转换的文件扩展名
    """
    if output_dir is None:
        output_dir = input_dir
    
    converted_files = []
    
    for filename in os.listdir(input_dir):
        if filename.endswith(extension):
            html_path = os.path.join(input_dir, filename)
            try:
                md_path = html_to_md(html_path, output_dir)
                converted_files.append(md_path)
                print(f"转换成功: {filename} -> {os.path.basename(md_path)}")
            except Exception as e:
                print(f"转换失败 {filename}: {str(e)}")
    
    print(f"\n转换完成! 共处理 {len(converted_files)} 个文件")
    print(f"输出目录: {output_dir}")

if __name__ == "__main__":
    # 配置路径（按需修改）
    HTML_DIR = r"C:\Users\chru\Desktop\merge"    # HTML文件所在目录
    OUTPUT_DIR = HTML_DIR    # Markdown输出目录
    
    # 执行批量转换
    batch_convert_html_to_md(
        input_dir=HTML_DIR,
        output_dir=OUTPUT_DIR,
        extension='.html'       # 可改为 '.htm'
    )