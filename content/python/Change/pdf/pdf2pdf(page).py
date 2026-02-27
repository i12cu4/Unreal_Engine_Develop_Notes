import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf_and_save(pdf_path, output_folder):
    # 创建新文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 读取PDF文件
    pdf = PdfReader(pdf_path)

    # 遍历PDF的每一页
    for page_number, page in enumerate(pdf.pages, start=1):
        # 创建新的PDF写入器
        pdf_writer = PdfWriter()

        # 将当前页面添加到新的PDF写入器
        pdf_writer.add_page(page)

        # 构建新的PDF文件名，形如：output_folder/1.pdf，2.pdf，...
        output_pdf_path = os.path.join(output_folder, f"{page_number}.pdf")

        # 将当前页面保存到新文件中
        with open(output_pdf_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)

# 使用示例
pdf_file_path = 'C:/Users/i12cu84/filename.pdf'
output_folder_path = 'C:/Users/i12cu84/dir'

split_pdf_and_save(pdf_file_path, output_folder_path)
