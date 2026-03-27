import os
import re
import html
from bs4 import BeautifulSoup
from datetime import datetime

# ==================== 配置区 ====================
HTML_FILE_PATH = r"C:\Users\Admin\Desktop\tk\t3.html"  # ← 请修改为您的HTML文件路径
OUTPUT_BASE_DIR = "zhihu_answers_export"
# ==============================================

def clean_filename(text, max_length=80):
    """清理文件名：移除非法字符，限制长度"""
    if not text:
        return "无标题"
    cleaned = re.sub(r'[\\/:*?"<>|\x00-\x1f\x7f-\x9f]', '', text)
    cleaned = cleaned.strip(' .,;:!?。！？，；：、-_')
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned[:max_length].rstrip(' .,;:!?') or "无标题"


def format_publish_time(time_str):
    """标准化时间为'年.月.日'格式（月日严格补零：2020.08.04）"""
    if not time_str or time_str == '未找到发布时间':
        return "未知时间"
    
    time_str = re.sub(r'[发布于编辑于发表于最后编辑于\s]', '', time_str)
    
    # 优先尝试标准日期解析（补零核心）
    patterns = [
        (r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日]?', '%Y-%m-%d'),
        (r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', '%Y-%m-%d'),
        (r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', '%m-%d-%Y')
    ]
    
    for pattern, fmt in patterns:
        match = re.search(pattern, time_str)
        if match:
            try:
                groups = list(match.groups())
                if len(groups[0]) == 2:  # 两位年份转四位
                    groups[0] = '20' + groups[0] if int(groups[0]) < 50 else '19' + groups[0]
                date_str = f"{groups[0]}-{int(groups[1]):02d}-{int(groups[2]):02d}"
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                # ✅ 关键修改：月日严格补零
                return f"{dt.year}.{dt.month:02d}.{dt.day:02d}"
            except:
                continue
    
    # 兜底：提取数字并补零
    match = re.search(r'(\d{4})[^\d]?(\d{1,2})[^\d]?(\d{1,2})', time_str)
    if match:
        try:
            y, m, d = match.groups()
            # ✅ 关键修改：兜底方案同样补零
            return f"{y}.{int(m):02d}.{int(d):02d}"
        except:
            pass
    return "未知时间"


def process_answer_content(content):
    """处理回答：单行化 + 按句尾标点分句（句间空一行）"""
    single_line = re.sub(r'\s+', ' ', content).strip()
    # 按中文/英文句尾标点分割（保留标点）
    sentences = re.split(r'(?<=[。！？.!?])', single_line)
    cleaned = [s.strip() for s in sentences if s.strip() and not re.match(r'^[.!?。！？]+$', s)]
    return '\n\n'.join(cleaned)  # 每句后双换行 → 句间空一行


def extract_zhihu_content(html_content):
    """提取知乎问答数据（逻辑保持不变）"""
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    containers = (
        soup.find_all('div', attrs={'itemtype': 'http://schema.org/Answer'}) or
        soup.find_all('div', class_=re.compile(r'AnswerItem|ContentItem|List-item', re.I))
    )
    
    for item in containers:
        # 标题提取
        title = None
        for sel in [('h2', {'class': re.compile(r'ContentItem-title', re.I)}),
                    ('div', {'class': re.compile(r'Question.*title', re.I)}),
                    ('a', {'class': re.compile(r'title', re.I)})]:
            elem = item.find(*sel)
            if elem:
                link = elem if elem.name == 'a' else elem.find('a')
                title = html.unescape((link or elem).get_text(strip=True))
                break
        
        # 回答内容提取
        content = None
        for sel in [('div', {'class': re.compile(r'RichContent-inner|ContentItem-content', re.I)}),
                    ('span', {'class': re.compile(r'RichText', re.I)}),
                    ('div', {'itemprop': 'text'})]:
            elem = item.find(*sel)
            if elem:
                for bad in elem.select('div.RichContent-copyright, div.RichContent-notice, script, style, footer'):
                    bad.decompose()
                content = html.unescape(elem.get_text(separator='\n', strip=True))
                break
        
        # 时间提取
        pub_time = None
        meta = item.find('meta', itemprop='datePublished')
        if meta and meta.get('content'):
            pub_time = meta['content'].split('T')[0]
        else:
            for sel in [('span', {'class': re.compile(r'time|date', re.I)}),
                        ('div', {'class': re.compile(r'time|date', re.I)})]:
                elem = item.find(*sel)
                if elem:
                    pub_time = elem.get_text(strip=True)
                    break
        
        if title and content:
            results.append({
                'question_title': title.strip(),
                'answer_content': content.strip(),
                'publish_time': pub_time.strip() if pub_time else '未找到发布时间'
            })
    return results


def read_html_file(path):
    """智能读取HTML（自动处理编码）"""
    for enc in ['utf-8', 'gbk', 'gb2312', 'latin1']:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    raise Exception(f"无法读取文件: {path}")


def main():
    os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
    
    print(f"📂 读取文件: {HTML_FILE_PATH}")
    try:
        html_content = read_html_file(HTML_FILE_PATH)
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return
    
    print("🔍 解析HTML内容...")
    results = extract_zhihu_content(html_content)
    if not results:
        print("⚠️  未提取到有效内容")
        return
    
    print(f"✓ 成功提取 {len(results)} 个问答")
    
    used_filenames = set()
    stats = {}
    
    for idx, qa in enumerate(results, 1):
        # ✅ 获取补零后的日期（如 2020.08.04）
        time_str = format_publish_time(qa['publish_time'])
        
        # 提取年份用于归档（从补零日期中取前4位）
        year_dir = "未知年份"
        if time_str != "未知时间":
            match = re.match(r'^(\d{4})', time_str)
            year_dir = match.group(1) if match else "未知年份"
        
        # 生成文件名（含补零日期）
        clean_title = clean_filename(qa['question_title'])
        base_name = f"{time_str}{clean_title}"
        filename = f"{base_name}.txt"
        counter = 1
        while filename in used_filenames:
            filename = f"{base_name}({counter}).txt"
            counter += 1
        used_filenames.add(filename)
        
        # 处理回答内容（单行+句间空行）
        processed_content = process_answer_content(qa['answer_content'])
        
        # 保存到对应年份目录
        year_path = os.path.join(OUTPUT_BASE_DIR, year_dir)
        os.makedirs(year_path, exist_ok=True)
        file_path = os.path.join(year_path, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            stats[year_dir] = stats.get(year_dir, 0) + 1
            print(f"[{idx}/{len(results)}] ✓ 保存: {year_dir}/{filename}")
        except Exception as e:
            print(f"[{idx}/{len(results)}] ✗ 保存失败 {filename}: {e}")
    
    # 输出统计
    print("\n" + "="*50)
    print("✅ 导出完成！文件分布统计:")
    for year in sorted(stats.keys()):
        print(f"  📁 {year}/ : {stats[year]} 个文件")
    print(f"📁 全部文件路径: ./{OUTPUT_BASE_DIR}/")
    print("="*50)


if __name__ == "__main__":
    try:
        import bs4
    except ImportError:
        print("❌ 请先安装: pip install beautifulsoup4")
        exit(1)
    main()