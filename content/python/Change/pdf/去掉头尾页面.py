import PyPDF2

def remove_first_last_pages(input_pdf_path, output_pdf_path):
    # 打开输入的PDF文件
    with open(input_pdf_path, 'rb') as input_pdf:
        # 读取PDF文件内容
        pdf_reader = PyPDF2.PdfReader(input_pdf)
        num_pages = len(pdf_reader.pages)
        
        # 创建一个新的PDF文件
        pdf_writer = PyPDF2.PdfWriter()
        
        # 检查是否需要删除第一页和最后一页
        if num_pages > 2:
            # 跳过第一页和最后一页，从第二页开始，直到倒数第二页
            for i in range(1, num_pages - 1):# *改动处
                page = pdf_reader.pages[i]
                pdf_writer.add_page(page)
        else:
            print("PDF文件只有1页或2页，无法删除任何页")
        
        # 保存新的PDF文件
        with open(output_pdf_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)

# 示例
remove_first_last_pages("input.pdf", "output.pdf")
