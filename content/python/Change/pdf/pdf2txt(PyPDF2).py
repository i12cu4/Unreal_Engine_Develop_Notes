import os
import PyPDF2

def convert_pdf_to_txt(pdf_path):    
    # 获取文件名（无扩展名）
    file_name = os.path.splitext(os.path.basename(pdf_path))[0]
    # 创建txt文件的完整路径
    txt_path = os.path.join(os.path.dirname(pdf_path), file_name + '.txt')

    # 打开PDF文件
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # 获取PDF的总页数
        num_pages = len(reader.pages)
        
        # 准备一个空列表来保存所有页面的文本
        all_text = []
        
        # 遍历每一页
        for page_num in range(num_pages):
            # 获取页面
            page = reader.pages[page_num]
            
            # 使用PyPDF2库本身来提取文本
            text = page.extract_text()
            
            # 将文本内容添加到列表中
            all_text.append(text)
        
        # 将所有页面的文本合并为一个字符串
        merged_text = ''.join(all_text)
        
        # 将合并后的文本写入到txt文件中
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(merged_text)

# 调用函数，传入PDF路径和输出TXT路径
#convert_pdf_to_txt('example.pdf')

import os

def get_pdf_files(root_dir):
    # 列出目录中的所有文件和文件夹
    files = os.listdir(root_dir)
    
    # 过滤出所有PDF文件
    pdf_files = [f for f in files if os.path.splitext(f)[1] == '.pdf']
    
    return pdf_files

# 调用函数，传入脚本根目录
root_dir = r"C:\Users\chru\Desktop\123"
pdf_files = get_pdf_files(root_dir)
print(pdf_files)
for temp in pdf_files:
    convert_pdf_to_txt(os.path.join(root_dir, temp))

print('done to pdf cast to txt')