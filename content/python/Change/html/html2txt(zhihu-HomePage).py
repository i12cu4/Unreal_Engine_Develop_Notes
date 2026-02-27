import os
from bs4 import BeautifulSoup

def extract_zhihu_content(html_path):
    """提取知乎主页的提问和回答内容"""
    try:
        # 读取HTML文件
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # 提取提问内容
        question_items = soup.select('.Profile-main .List .List-item:has(.ContentItem-meta)')
        for item in question_items:
            meta = item.select_one('.ContentItem-meta')
            if meta and '提问' in meta.text:
                title = item.select_one('.ContentItem-title') or item.select_one('.Post-Title')
                content = item.select_one('.RichContent-inner') or item.select_one('.Post-RichText')
                if title and content:
                    results.append(f"【提问】{title.get_text(strip=True)}\n{content.get_text(strip=True)}\n")
        
        # 提取回答内容
        answer_items = soup.select('.Profile-main .List .List-item:has(.ContentItem-actions)')
        for item in answer_items:
            if item.select_one('.ContentItem-meta') and '回答' in item.select_one('.ContentItem-meta').text:
                question = item.select_one('.QuestionItem-title') or item.select_one('.ContentItem-title')
                content = item.select_one('.RichContent-inner') or item.select_one('.Post-RichText')
                if question and content:
                    results.append(f"【回答】{question.get_text(strip=True)}\n{content.get_text(strip=True)}\n")
        
        return '\n'.join(results)
    
    except Exception as e:
        return f"处理过程中出错: {str(e)}"

def process_html_directory(directory):
    """处理目录下所有HTML文件"""
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            html_path = os.path.join(directory, filename)
            txt_path = os.path.splitext(html_path)[0] + '.txt'
            
            content = extract_zhihu_content(html_path)
            
            # 写入TXT文件
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已生成: {txt_path}")

if __name__ == "__main__":
    target_directory = r"C:\Users\chru\Desktop\merge"
    if os.path.exists(target_directory):
        process_html_directory(target_directory)
        print("处理完成！")
    else:
        print("目录不存在，请检查路径")