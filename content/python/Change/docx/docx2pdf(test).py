#Word转Pdf (coding) 指定字体版
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 获取当前工作目录
current_directory = os.getcwd()

# 字体文件的路径
font_path = os.path.join(current_directory, 'yahei.ttf')

# 注册字体
pdfmetrics.registerFont(TTFont('YaHei', font_path))

def docx_to_pdf(docx_path, pdf_path):
    # 加载文档
    doc = Document(docx_path)
    pdf_file = open(pdf_path, "wb")

    # 创建PDF和画布
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter  # 获取letter纸张大小

    # 遍历文档中的每一段，写入PDF
    for para in doc.paragraphs:
        # 使用注册的字体
        c.setFont('YaHei', 10)  # 这里使用注册的字体
        c.drawString(100, height - 100, para.text)
        height -= 20  # 下移一段的距离

    # 保存PDF
    c.save()
    pdf_file.close()

def convert_docs_to_pdf(directory):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith(".docx"):
            # 构建完整的文件路径
            docx_path = os.path.join(directory, filename)
            # 构建PDF的文件路径
            pdf_path = os.path.join(directory, filename.replace(".docx", ".pdf"))
            # 调用转换函数
            print(f'Converting {filename} to {filename.replace(".docx", ".pdf")}')

            docx_to_pdf(docx_path, pdf_path)
            print(f"Converted {filename} to {filename.replace('.docx', '.pdf')}")

# 指定要转换的目录
directory = 'C:/Users/i12cu84/ocr/'
convert_docs_to_pdf(directory)
