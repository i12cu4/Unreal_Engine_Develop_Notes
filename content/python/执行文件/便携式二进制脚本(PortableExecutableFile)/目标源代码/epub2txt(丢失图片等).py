import os
import sys
from pathlib import Path
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
        print(f"读取EPUB文件错误 {epub_path}: {e}")
        return None

def save_content_to_txt(content, txt_path):
    try:
        # 将文本内容保存到同名的 TXT 文件中
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(content)
        print(f"内容已保存到: {txt_path}")
        return True
    except Exception as e:
        print(f"保存内容到 {txt_path} 时出错: {e}")
        return False

def main():
    # 检查是否有文件被拖拽到脚本上
    if len(sys.argv) < 2:
        input("请将EPUB文件拖拽到此脚本上，然后按回车键...")
        return
    
    # 处理所有拖拽的文件
    for file_path in sys.argv[1:]:
        path = Path(file_path)
        
        # 检查文件是否存在
        if not path.exists():
            print(f"文件不存在: {file_path}")
            continue
        
        # 检查是否为EPUB文件
        if path.suffix.lower() != '.epub':
            print(f"跳过非EPUB文件: {file_path}")
            continue
        
        # 生成TXT文件路径
        txt_path = path.with_suffix('.txt')
        
        # 检查TXT文件是否已存在
        if txt_path.exists():
            print(f"TXT文件已存在，跳过: {txt_path}")
            continue
        
        # 提取内容并保存到TXT文件
        print(f"正在处理: {path.name}")
        content = extract_epub_content(str(path))
        if content:
            save_content_to_txt(content, str(txt_path))

if __name__ == "__main__":
    main()
    print("\n处理完成!")
    input("按回车键退出...")