import os
import fitz  # PyMuPDF
from PIL import Image

def pdf_to_images_and_save(pdf_path, output_folder):
    # 创建新文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 打开 PDF 文件
    pdf_document = fitz.open(pdf_path)

    # 遍历每一页
    for page_number in range(pdf_document.page_count):
        # 获取页面对象
        page = pdf_document[page_number]

        # 获取页面的图像
        image_list = page.get_pixmap()

        # 将 Pixmap 转换为 PIL Image
        image = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)

        # 保存图像为 PNG 文件
        image_path = os.path.join(output_folder, f"{page_number + 1}.png")
        image.save(image_path, "PNG")

# 使用示例
pdf_file_path = 'C:/Users/i12cu84/filename.pdf'
output_folder_path = 'C:/Users/i12cu84/dir'

pdf_to_images_and_save(pdf_file_path, output_folder_path)
