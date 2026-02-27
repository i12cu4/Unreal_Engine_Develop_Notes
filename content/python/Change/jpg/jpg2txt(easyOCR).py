import os
import easyocr
import cv2
import numpy as np
from glob import glob
import time
from PIL import Image

# ================= 用户配置区域 =================
# 设置输入目录（包含JPG/JPEG图片的目录）
JPEG_DIR = r"C:\Users\chru\Desktop\123"

# 设置输出目录（Markdown文件将保存到这里）
HTML_DIR = JPEG_DIR

# EasyOCR 配置
LANGUAGES = ['ch_sim', 'en']  # 简体中文 + 英文
USE_GPU = False  # 如果没有NVIDIA GPU请设置为False

# 长图处理参数
MAX_CHUNK_HEIGHT = 1000  # 每个块的最大高度（像素）
OVERLAP = 100            # 块之间的重叠区域（像素）
SCALE_FACTOR = 2.0       # 图像放大倍数（提高小文字识别率）
# ===============================================

# 初始化EasyOCR阅读器（首次运行会自动下载模型）
def get_reader():
    print("正在初始化EasyOCR...")
    start_time = time.time()
    reader = easyocr.Reader(LANGUAGES, gpu=USE_GPU)
    print(f"EasyOCR初始化完成，耗时: {time.time() - start_time:.2f}秒")
    return reader

def preprocess_image(image_path, scale_factor=1.0):
    """图像预处理以提高识别精度"""
    try:
        # 使用PIL打开图片（解决中文路径问题）
        pil_image = Image.open(image_path)
        
        # 放大图像（提高小文字识别率）
        if scale_factor > 1.0:
            new_width = int(pil_image.width * scale_factor)
            new_height = int(pil_image.height * scale_factor)
            pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
        
        img = np.array(pil_image)
        
        # 如果是RGBA图像，转换为RGB
        if len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        
        # 转换为OpenCV格式 (BGR)
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # 转换为灰度图
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # 使用自适应直方图均衡化增强对比度
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16, 16))
        enhanced = clahe.apply(gray)
        
        # 自适应阈值二值化（处理光照不均）
        thresh = cv2.adaptiveThreshold(
            enhanced, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # 降噪处理
        denoised = cv2.medianBlur(thresh, 3)
        
        # 形态学操作增强文本
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    except Exception as e:
        print(f"图片预处理出错: {str(e)}")
        return None

def split_long_image(image, max_height, overlap):
    """将长图分割成多个小块"""
    chunks = []
    height = image.shape[0]
    
    # 如果图像高度小于最大块高度，直接返回整个图像
    if height <= max_height:
        return [image]
    
    # 计算分割点
    start = 0
    while start < height:
        end = min(start + max_height, height)
        chunk = image[start:end, :]
        chunks.append(chunk)
        
        # 移动到下一个块（考虑重叠）
        start = end - overlap
        if start >= height - overlap:  # 避免最后一个块太小
            break
    
    print(f"将长图分割为 {len(chunks)} 个块 (高度: {max_height}px, 重叠: {overlap}px)")
    return chunks

def extract_text_from_image(reader, image_path):
    """使用EasyOCR从图片中提取文本（支持长图）"""
    try:
        # 图像预处理（放大图像）
        processed_img = preprocess_image(image_path, SCALE_FACTOR)
        
        if processed_img is None:
            # 如果预处理失败，尝试直接读取图片
            pil_image = Image.open(image_path)
            if SCALE_FACTOR > 1.0:
                new_width = int(pil_image.width * SCALE_FACTOR)
                new_height = int(pil_image.height * SCALE_FACTOR)
                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
            processed_img = np.array(pil_image.convert('L'))  # 转为灰度
        
        # 如果是长图，分割成多个小块
        if processed_img.shape[0] > MAX_CHUNK_HEIGHT:
            chunks = split_long_image(processed_img, MAX_CHUNK_HEIGHT, OVERLAP)
        else:
            chunks = [processed_img]
        
        all_text = []
        
        # 处理每个块
        for i, chunk in enumerate(chunks):
            # 保存临时图像用于调试（可选）
            # cv2.imwrite(f"chunk_{i}.png", chunk)
            
            # 使用EasyOCR识别文本
            results = reader.readtext(
                chunk, 
                detail=0, 
                paragraph=True,
                batch_size=1,  # 减少内存使用
                text_threshold=0.4,  # 降低阈值以识别更多文本
                width_ths=0.8,  # 放宽宽度阈值
                decoder='beamsearch',  # 使用beamsearch提高准确性
                blocklist='=-+*#$%^&@~`'  # 过滤特殊字符
            )
            
            # 合并识别结果
            chunk_text = "\n".join(results).strip()
            if chunk_text:
                all_text.append(chunk_text)
                print(f"  块 {i+1}/{len(chunks)} 识别到 {len(chunk_text)} 字符")
            else:
                print(f"  块 {i+1}/{len(chunks)} 未识别到文本")
        
        # 合并所有块的文本
        return "\n\n".join(all_text).strip()
    
    except Exception as e:
        print(f"处理图片时出错: {str(e)}")
        return ""

def process_images(reader):
    """处理指定目录下的所有图片"""
    # 确保输出目录存在
    if not os.path.exists(HTML_DIR):
        os.makedirs(HTML_DIR)
        print(f"已创建输出目录: {HTML_DIR}")
    
    # 获取所有图片文件（确保不重复）
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']:
        image_files.extend(glob(os.path.join(JPEG_DIR, ext)))
    
    # 去重处理
    image_files = list(set(image_files))
    
    if not image_files:
        print(f"在目录 {JPEG_DIR} 中未找到任何JPG/JPEG图片")
        return
    
    total_images = len(image_files)
    processed_count = 0
    success_count = 0
    
    print(f"找到 {total_images} 张图片需要处理")
    print("=" * 60)
    
    for img_path in image_files:
        try:
            filename = os.path.basename(img_path)
            print(f"处理: {filename}")
            
            # 获取图片尺寸
            with Image.open(img_path) as img:
                width, height = img.size
            print(f"  图片尺寸: {width}x{height} 像素")
            
            start_time = time.time()
            text = extract_text_from_image(reader, img_path)
            process_time = time.time() - start_time
            
            # 创建输出文件名（与图片同名）
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(HTML_DIR, f"{base_name}.md")
            
            # 保存到单独的Markdown文件
            with open(output_file, "w", encoding="utf-8") as md_file:
                md_file.write(text)
            
            char_count = len(text)
            print(f"  识别完成，耗时: {process_time:.2f}秒，字符数: {char_count}")
            
            if char_count > 0:
                success_count += 1
                print(f"  结果已保存到: {output_file}")
            else:
                print("  未识别到文本")
            
            print("-" * 60)
            processed_count += 1
            
        except Exception as e:
            print(f"处理 {img_path} 时出错: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"处理完成! 成功处理 {success_count}/{processed_count} 张图片")
    print(f"Markdown文件已保存到: {HTML_DIR}")

if __name__ == "__main__":
    # 检查输入目录是否存在
    if not os.path.exists(JPEG_DIR):
        print(f"错误: 输入目录不存在 - {JPEG_DIR}")
    else:
        reader = get_reader()
        process_images(reader)
        
        # 清理EasyOCR资源
        if hasattr(reader, 'model'):
            del reader.model
        if hasattr(reader, 'detector'):
            del reader.detector
        if hasattr(reader, 'recognizer'):
            del reader.recognizer