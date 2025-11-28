import os
import sys
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import html

def clean_epub_text(epub_path, pdf_path):
    """
    改进的EPUB到PDF转换，专门处理编码问题
    """
    try:
        # 读取EPUB文件
        book = epub.read_epub(epub_path)
        
        # 创建PDF
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4
        y_position = height - 50
        line_height = 14
        page_margin = 50
        
        # 设置中文字体（如果有的话）
        try:
            # 尝试使用系统字体
            c.setFont("Helvetica", 10)
        except:
            c.setFont("Helvetica", 10)
        
        def clean_text(text):
            """清理文本，移除乱码和重复字符"""
            if not text:
                return ""
            
            # 解码HTML实体
            text = html.unescape(text)
            
            # 移除连续的重复字符（如IIIIII）
            text = re.sub(r'([A-Z])\1{3,}', '', text)
            
            # 移除常见的乱码模式
            text = re.sub(r'[^\w\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef.,!?;:()\-—"\'`]', '', text)
            
            # 清理多余空格
            text = ' '.join(text.split())
            
            return text.strip()
        
        def add_text_to_pdf(text, canvas_obj, y_pos):
            """将文本添加到PDF，处理分页"""
            lines = text.split('\n')
            current_y = y_pos
            
            for line in lines:
                if not line.strip():
                    continue
                    
                cleaned_line = clean_text(line)
                if not cleaned_line:
                    continue
                
                # 处理长文本换行
                words = cleaned_line.split()
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    # 粗略估计文本宽度
                    if len(test_line) > 80:  # 如果行太长
                        if current_line:  # 先输出当前行
                            output_line = ' '.join(current_line)
                            if current_y < page_margin:
                                canvas_obj.showPage()
                                current_y = height - page_margin
                                c.setFont("Helvetica", 10)
                            canvas_obj.drawString(page_margin, current_y, output_line[:100])
                            current_y -= line_height
                        current_line = [word]
                    else:
                        current_line.append(word)
                
                # 输出剩余内容
                if current_line:
                    output_line = ' '.join(current_line)
                    if current_y < page_margin:
                        canvas_obj.showPage()
                        current_y = height - page_margin
                        c.setFont("Helvetica", 10)
                    canvas_obj.drawString(page_margin, current_y, output_line[:100])
                    current_y -= line_height
            
            return current_y
        
        # 提取并清理内容
        all_text = []
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    content = item.get_content().decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # 移除脚本和样式标签
                    for script in soup(["script", "style", "head", "meta", "link"]):
                        script.decompose()
                    
                    # 提取文本
                    text = soup.get_text(separator='\n', strip=True)
                    cleaned_text = clean_text(text)
                    
                    if cleaned_text:
                        all_text.append(cleaned_text)
                        
                except Exception as e:
                    print(f"处理章节时出错: {e}")
                    continue
        
        # 将清理后的文本添加到PDF
        current_y = y_position
        for text_chunk in all_text:
            current_y = add_text_to_pdf(text_chunk, c, current_y)
        
        c.save()
        print(f"成功转换: {epub_path} -> {pdf_path}")
        return True
        
    except Exception as e:
        print(f"转换失败 {epub_path}: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        input("请将EPUB文件拖拽到此脚本上，然后按回车键...")
        return
    
    for file_path in sys.argv[1:]:
        path = Path(file_path)
        if not path.exists():
            print(f"文件不存在: {file_path}")
            continue
        if path.suffix.lower() != '.epub':
            print(f"跳过非EPUB文件: {file_path}")
            continue
        
        pdf_path = path.with_suffix('.pdf')
        if pdf_path.exists():
            print(f"PDF文件已存在，跳过: {pdf_path}")
            continue
        
        print(f"正在转换: {path.name}")
        clean_epub_text(str(path), str(pdf_path))

if __name__ == "__main__":
    main()
    print("\n处理完成!")
    input("按回车键退出...")