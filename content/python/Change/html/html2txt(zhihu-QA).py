import os
import re
import unicodedata
from bs4 import BeautifulSoup
from datetime import datetime

def clean_filename(title):
    """清理文件名中的非法字符"""
    # 移除特殊字符和空格
    cleaned = re.sub(r'[\\/*?:"<>|\s]', '_', title)
    # 移除控制字符
    cleaned = ''.join(ch for ch in cleaned if unicodedata.category(ch)[0] != "C")
    # 限制文件名长度
    return cleaned[:100]  # 最大长度100个字符

def extract_zhihu_data(html_path, output_dir):
    """
    从知乎HTML文件中提取问答数据并保存为TXT文件
    :param html_path: HTML文件或目录路径
    :param output_dir: 输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 收集所有HTML文件路径
    html_files = []
    if os.path.isdir(html_path):
        for file in os.listdir(html_path):
            if file.endswith(".html"):
                html_files.append(os.path.join(html_path, file))
    elif os.path.isfile(html_path) and html_path.endswith(".html"):
        html_files.append(html_path)
    
    # 处理每个HTML文件
    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
            # 知乎回答块通常包含在特定的类中
            answer_blocks = soup.find_all('div', class_='List-item')
            
            for block in answer_blocks:
                try:
                    # 提取问题标题
                    question_title = block.find('h2', class_='ContentItem-title').get_text(strip=True)
                    
                    # 提取回答内容
                    answer_content = block.find('div', class_='RichContent-inner').get_text(strip=True)
                    
                    # 提取日期并格式化
                    date_element = block.find('div', class_='ContentItem-time')
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_element.get_text())
                    if not date_match:
                        continue
                    date_str = date_match.group()
                    formatted_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y.%m.%d')
                    
                    # 清理问题标题作为文件名
                    clean_title = clean_filename(question_title)
                    
                    # 生成文件名
                    filename = f"{formatted_date}{clean_title}.txt"
                    save_path = os.path.join(output_dir, filename)
                    
                    # 处理重名文件
                    counter = 1
                    while os.path.exists(save_path):
                        save_path = os.path.join(
                            output_dir, 
                            f"{formatted_date}{clean_title}_{counter}.txt"
                        )
                        counter += 1
                    
                    # 保存回答内容（仅回答内容，不含问题标题）
                    with open(save_path, 'w', encoding='utf-8') as out_f:
                        out_f.write(answer_content)
                        
                except (AttributeError, TypeError):
                    # 跳过解析失败的块
                    continue

if __name__ == "__main__":
    # 使用示例
    html_path = r"C:\Users\chru\Desktop\merge"  # 替换为你的HTML文件/目录路径
    output_dir = html_path  # 替换为输出目录
    
    extract_zhihu_data(html_path, output_dir)
    print(f"处理完成！文件已保存至：{output_dir}")