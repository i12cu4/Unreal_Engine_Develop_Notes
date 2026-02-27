import os
import sys
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np

def extract_chinese_with_paddle(image_path):
    """使用PaddleOCR提取中文文本"""
    try:
        print(f"正在处理图片: {image_path}")
        img = Image.open(image_path)
        img_array = np.array(img)
        
        print("初始化PaddleOCR...")
        # 使用中文模型
        ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        
        print("开始OCR识别...")
        result = ocr.ocr(img_array, cls=True)
        
        print("解析识别结果...")
        texts = []
        if result is not None:
            for line in result:
                if line and line[0]:
                    for word_info in line:
                        if word_info and word_info[1]:
                            text = word_info[1][0]
                            confidence = word_info[1][1]
                            texts.append(text)
                            print(f"识别到: '{text}' (置信度: {confidence:.2f})")
        
        if not texts:
            print("警告: 未提取到任何文本")
            return ""
        
        return "\n".join(texts)
    except Exception as e:
        print(f"PaddleOCR处理出错: {str(e)}")
        return ""

def process_images_paddle(input_dir):
    """处理目录中的所有图片"""
    supported_exts = ('.jpg', '.jpeg', '.png')
    processed_count = 0
    found_files = False

    print("\n扫描目录中的图片文件...")
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_exts):
            found_files = True
            image_path = os.path.join(input_dir, filename)
            print(f"\n{'='*50}")
            print(f"处理图片: {filename}")
            
            # 提取文本
            text = extract_chinese_with_paddle(image_path)
            
            if not text:
                print("警告: 未提取到任何文本")
            
            # 生成输出文件名
            base_name = os.path.splitext(filename)[0]
            txt_path = os.path.join(input_dir, f"{base_name}.txt")
            
            # 保存文本
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"文本已保存到: {txt_path}")
            processed_count += 1
    
    if not found_files:
        print("未找到任何图片文件 (.jpg/.jpeg/.png)")
    
    return processed_count

if __name__ == "__main__":
    # 设置输入目录
    JPEG_DIR = r"C:\Users\chru\Desktop\123"
    
    print("="*50)
    print("中文图片转文本工具 - PaddleOCR版")
    print("="*50)
    
    # 检查目录是否存在
    if not os.path.isdir(JPEG_DIR):
        print(f"错误: 目录不存在 - {JPEG_DIR}")
        sys.exit(1)
    
    print(f"输入目录: {JPEG_DIR}")
    print(f"输出目录: {JPEG_DIR}")
    print("="*50)
    
    try:
        count = process_images_paddle(JPEG_DIR)
        print("\n" + "="*50)
        print(f"处理完成! 共转换 {count} 个图片文件")
        print("="*50)
    except Exception as e:
        print("\n" + "!"*50)
        print(f"程序运行出错: {str(e)}")
        print("可能原因:")
        print("1. 网络问题导致模型下载失败")
        print("2. 缺少依赖库")
        print("安装依赖: pip install paddlepaddle paddleocr pillow numpy")
        print("!"*50)
        sys.exit(1)

