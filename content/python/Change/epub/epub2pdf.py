import os
import pypandoc

def convert_epub_to_pdf(epub_path, pdf_path):
    # 创建PDF文件
    pdf_filename = os.path.splitext(os.path.basename(epub_path))[0] + ".pdf"
    pdf_file_path = os.path.join(pdf_path, pdf_filename)

    # 使用pandoc将EPUB转换为PDF，选择xelatex引擎，并指定字体
    extra_args = ['--pdf-engine=xelatex', '--pdf-engine-opt=-8bit', '--variable', 'mainfont=NotoSerifCJKsc-Regular.otf', '--dpi=300']
    pypandoc.convert_file(epub_path, "pdf", outputfile=pdf_file_path, extra_args=extra_args)

    print(f"转换完成: {pdf_file_path}")

def convert_epubs_to_pdfs(epub_folder, pdf_folder):
    # 确保PDF文件夹存在
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)

    # 遍历epub文件夹
    for root, dirs, files in os.walk(epub_folder):
        for file in files:
            if file.endswith(".epub"):
                epub_path = os.path.join(root, file)
                convert_epub_to_pdf(epub_path, pdf_folder)
convert_epubs_to_pdfs("C:/Users/i12cu84/Desktop/tianya/more/epub", "C:/Users/i12cu84/Desktop/tianya/more/epub")

