import os
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_epub_content(epub_path):
    try:
        # 读取 EPUB 文件
        book = epub.read_epub(epub_path)
        
        # 提取文本内容
        content = ""
        for item in book.get_items_of_type(9):  # Type 9 corresponds to documents in EPUB (text content)
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text_content = soup.get_text()
            content += text_content + '\n'
        
        return content
    except Exception as e:
        print(f"Error reading EPUB file {epub_path}: {e}")
        return None

def save_content_to_txt(content, txt_path):
    try:
        # 将文本内容保存到同名的 TXT 文件中
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(content)
        print(f"Content saved to {txt_path}")
    except Exception as e:
        print(f"Error saving content to {txt_path}: {e}")

def process_epubs_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".epub"):
                epub_path = os.path.join(root, file)
                txt_path = os.path.splitext(epub_path)[0] + ".txt"
                
                # 提取内容并保存到同名的 TXT 文件中
                content = extract_epub_content(epub_path)
                if content:
                    save_content_to_txt(content, txt_path)

# 指定要处理的文件夹路径
folder_to_process =  'C:/Users/i12cu84/epub'

# 执行处理
process_epubs_in_folder(folder_to_process)
