import os
from PIL import Image
import pytesseract

# 设置路径变量
base_dir = r"C:\Users\chru\Desktop\123"

# 设置 Tesseract 的安装路径（根据您的实际安装位置修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program File\Tesseract-OCR\tesseract.exe'

def convert_jpg_to_txt(directory):
    """
    将指定目录下的所有JPG文件通过OCR转换为TXT文件（支持中文）
    :param directory: 包含JPG文件的目录，也将用于保存TXT文件
    """
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        # 检查文件是否为JPG格式（不区分大小写）
        if filename.lower().endswith(('.jpg', '.jpeg')):
            input_path = os.path.join(directory, filename)
            # 创建输出文件名（相同名称，扩展名改为.txt）
            output_filename = os.path.splitext(filename)[0] + '.txt'
            output_path = os.path.join(directory, output_filename)
            
            try:
                # 打开图像文件
                img = Image.open(input_path)
                
                # 使用Tesseract进行中文OCR识别
                # 'chi_sim'表示简体中文
                text = pytesseract.image_to_string(img, lang='chi_sim')
                
                # 将识别结果写入文本文件（UTF-8编码）
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                print(f"转换成功: {filename} -> {output_filename}")
                
            except Exception as e:
                print(f"处理 {filename} 时出错: {str(e)}")

if __name__ == "__main__":
    # 执行转换
    convert_jpg_to_txt(base_dir)
    print("所有JPG文件转换完成！")