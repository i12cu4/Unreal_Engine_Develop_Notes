import os
import easyocr

def process_png_directory(png_folder, txt_filename):
    # 初始化 EasyOCR
    reader = easyocr.Reader(['ch_sim'])  # 默认语言设置为中文，根据需要可以更改

    # 获取 PNG 文件列表并按数字排序
    png_files = sorted([f for f in os.listdir(png_folder) if f.lower().endswith('.png')], key=lambda x: int(os.path.splitext(x)[0]))

    # 遍历 PNG 文件
    with open(txt_filename, 'a', encoding='utf-8') as txt_file:
        for png_file in png_files:
            # 构建 PNG 文件的绝对路径
            png_path = os.path.join(png_folder, png_file)

            # 使用 EasyOCR 识别图片内容
            text = reader.readtext(png_path)

            # 将识别的内容写入 txt 文件
            txt_file.write(f"\n\n{png_file}:\n")
            txt_file.write('\n'.join([result[1] for result in text]))

# 使用示例

png_folder_path =  'C:/Users/i12cu84/666/'
txt_file_name = 'C:/Users/i12cu84/file.txt'

process_png_directory(png_folder_path, txt_file_name)
