#pdf转txt(用ocr识别图片) gpu处理 

# 设置 EasyOCR 使用 GPU 加入此句
reader = easyocr.Reader(['ch_sim'], gpu=True)

#其余代码使用 PdfToTxtWithOcrByCpu(images).py 不做变化即可