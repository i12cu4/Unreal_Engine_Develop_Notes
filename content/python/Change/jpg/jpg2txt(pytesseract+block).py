import os
import pytesseract
import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm
import unicodedata
import shutil

# 设置Tesseract路径 下载地址https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r'C:\Program File\Tesseract-OCR\tesseract.exe'

def normalize_filename(filename):
    """规范化文件名，保留中文和常用标点"""
    # 允许的字符：中文、字母、数字、空格、下划线、点、括号、破折号
    allowed_chars = (
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        ' _-.,()（）【】[]{}·~@#$%^&+=!'
    )
    
    # 保留中文字符 (Unicode范围: 4E00-9FFF)
    cleaned = ''.join(
        c if ('\u4e00' <= c <= '\u9fff') or c in allowed_chars else '_'
        for c in filename
    )
    
    # 替换连续多个下划线为单个
    cleaned = re.sub(r'_+', '_', cleaned)
    return cleaned

def safe_read_image(image_path):
    """安全读取图像，处理路径中的特殊字符"""
    try:
        # 尝试使用OpenCV读取
        img = cv2.imread(image_path)
        if img is not None:
            return img
        
        # 如果OpenCV失败，尝试使用PIL
        with Image.open(image_path) as pil_img:
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            return img
    except Exception as e:
        # 作为最后手段，尝试复制文件并重命名
        try:
            print(f"尝试复制并重命名文件: {os.path.basename(image_path)}")
            temp_dir = os.path.join(os.path.dirname(image_path), "temp_ocr")
            os.makedirs(temp_dir, exist_ok=True)
            
            # 规范化文件名
            normalized_name = normalize_filename(os.path.basename(image_path))
            temp_path = os.path.join(temp_dir, normalized_name)
            
            # 复制文件
            shutil.copy2(image_path, temp_path)
            
            # 再次尝试读取
            img = cv2.imread(temp_path)
            if img is not None:
                return img
                
            # 如果仍然失败，使用PIL
            with Image.open(temp_path) as pil_img:
                return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e2:
            raise ValueError(f"无法读取图像: {os.path.basename(image_path)} - 原因: {str(e2)}")
        finally:
            # 清理临时文件
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

def enhance_image_quality(img):
    """
    高级图像增强处理
    专注于提高汉字识别精度
    """
    # 1. 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. 自适应直方图均衡化（增强对比度）
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16, 16))
    equalized = clahe.apply(gray)
    
    # 3. 锐化处理 - 强化汉字笔画
    sharpen_kernel = np.array([[0, -1, 0],
                              [-1, 5, -1],
                              [0, -1, 0]])
    sharpened = cv2.filter2D(equalized, -1, sharpen_kernel)
    
    # 4. 去噪处理（保留边缘）
    denoised = cv2.bilateralFilter(sharpened, 9, 75, 75)
    
    # 5. 自适应阈值二值化
    binary = cv2.adaptiveThreshold(
        denoised, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 31, 10
    )
    
    return binary

def calculate_block_height(img_height):
    """根据图像高度计算合适的分块高度"""
    if img_height <= 5000:
        return 1000
    elif img_height <= 10000:
        return 1500
    else:
        return 2000

def preprocess_long_image(image_path):
    """
    针对超长图片的优化预处理流程
    :param image_path: 图片路径
    :return: 处理后的图像块列表
    """
    # 使用安全方式读取图像
    img = safe_read_image(image_path)
    original_height, original_width = img.shape[:2]
    
    # 图像质量增强
    processed = enhance_image_quality(img)
    
    # 图像分割 - 将超长图片分成多个块
    block_height = calculate_block_height(original_height)
    overlap = 100  # 块之间的重叠区域
    height, width = processed.shape
    
    blocks = []
    start_y = 0
    
    print(f"图像尺寸: {original_width}x{original_height}, 分块高度: {block_height}, 重叠区域: {overlap}")
    
    while start_y < height:
        end_y = min(start_y + block_height, height)
        
        # 提取当前块（带重叠区域）
        block_start = max(0, start_y - overlap)
        block_end = min(height, end_y + overlap)
        block = processed[block_start:block_end, 0:width]
        
        # 转换为PIL格式
        block_pil = Image.fromarray(block)
        blocks.append(block_pil)
        
        # 更新位置
        start_y = end_y
    
    print(f"分割为 {len(blocks)} 个图像块")
    return blocks

def optimize_ocr_config():
    """
    优化OCR配置，专注于中文识别
    """
    config = (
        r'--oem 1 '               # 使用LSTM引擎
        r'--psm 6 '               # 单列文本模式
        r'-c preserve_interword_spaces=1 '  # 保留空格
        r'-c textord_old_baselines=1 '      # 旧版基线检测
        r'-c language_model_penalty_non_freq_dict_word=0.1 '  # 降低非高频词惩罚
        r'-c textord_min_linesize=1.5 '     # 更小的行尺寸
        r'-c tessedit_char_blacklist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/~`'  # 黑名单英文字符
    )
    return config

def ocr_image_block(block):
    """对单个图像块进行OCR识别"""
    # OCR配置
    config = optimize_ocr_config()
    
    # 尝试不同的识别策略
    results = []
    
    # 策略1: 标准识别
    text1 = pytesseract.image_to_string(
        block, 
        lang='chi_sim',  # 仅中文
        config=config
    )
    results.append(text1)
    
    # 策略2: 轻微旋转图像后识别
    for angle in [-1, 0, 1]:
        rotated = block.rotate(angle, fillcolor=255)
        text = pytesseract.image_to_string(
            rotated, 
            lang='chi_sim',
            config=config
        )
        results.append(text)
    
    # 选择汉字最多的结果
    best_text = ""
    max_hanzi = 0
    for text in results:
        hanzi_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        if hanzi_count > max_hanzi:
            max_hanzi = hanzi_count
            best_text = text
    
    return best_text

def ocr_with_high_accuracy(image_blocks, filename):
    """
    高精度OCR识别
    :param image_blocks: 分块后的图像列表
    :param filename: 当前处理的文件名
    :return: 识别出的文本
    """
    full_text = []
    
    print(f"开始OCR处理: {filename} ({len(image_blocks)} 个图像块)...")
    
    for i, block in enumerate(tqdm(image_blocks, desc=f"OCR进度 {filename[:15]}...")):
        try:
            # 识别当前块
            text = ocr_image_block(block)
            
            # 后处理：移除可能的重复行（来自重叠区域）
            if i > 0 and full_text:
                last_lines = full_text[-1].strip().split('\n')[-2:]  # 取最后2行
                current_lines = text.strip().split('\n')[:2]         # 取开头2行
                
                # 检查重叠区域
                if last_lines and current_lines:
                    # 比较最后几行和开头几行
                    last_chunk = "\n".join(last_lines)
                    first_chunk = "\n".join(current_lines)
                    
                    # 如果相似度高，移除重复行
                    if last_chunk and first_chunk and last_chunk == first_chunk:
                        text = '\n'.join(text.split('\n')[len(current_lines):])
            
            full_text.append(text)
            
        except Exception as e:
            print(f"块 {i+1} 识别失败: {str(e)}")
            full_text.append(f"[识别失败块 {i+1}: {str(e)}]")
    
    # 合并文本
    result = "\n".join(full_text)
    
    # 后处理：移除多余空行
    cleaned_result = "\n".join(line.strip() for line in result.splitlines() if line.strip())
    
    return cleaned_result

def convert_long_jpg_to_txt(input_dir):
    """
    转换指定目录下的所有长图JPG文件为TXT
    结果文件保存在原始图片所在目录
    """
    # 获取所有支持的图像文件
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    image_files = [f for f in os.listdir(input_dir) 
                 if f.lower().endswith(valid_extensions)]
    
    if not image_files:
        print(f"在 {input_dir} 中未找到图像文件")
        return
    
    print(f"找到 {len(image_files)} 个图像文件，开始处理超长图片...")
    success_count = 0
    fail_count = 0
    
    for img_file in tqdm(image_files, desc="总进度"):
        input_path = os.path.join(input_dir, img_file)
        
        try:
            # 1. 预处理：分块+增强
            blocks = preprocess_long_image(input_path)
            
            # 2. 高精度OCR
            text = ocr_with_high_accuracy(blocks, img_file)
            
            # 3. 构建输出路径（与原始图片相同目录）
            base_name = os.path.splitext(img_file)[0]
            output_path = os.path.join(input_dir, f"{base_name}.txt")
            
            # 4. 保存结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"\n转换完成: {img_file}")
            print(f"字符数: {len(text)}")
            print(f"输出位置: {output_path}")
            success_count += 1
            
        except Exception as e:
            print(f"\n处理文件 {img_file} 失败: {str(e)}")
            fail_count += 1
            # 保存错误日志到原始目录
            log_path = os.path.join(input_dir, "ocr_error_log.txt")
            with open(log_path, 'a', encoding='utf-8') as log:
                log.write(f"{img_file}: {str(e)}\n")
    
    print(f"\n{'='*50}")
    print(f"处理完成! 成功: {success_count}, 失败: {fail_count}")
    print(f"所有结果文件保存在: {input_dir}")

if __name__ == "__main__":
    input_dir = r"C:\Users\chru\Desktop\123"
    
    # 在文件顶部导入re模块
    import re
    
    # 替换原来的convert_long_jpg_to_txt调用
    convert_long_jpg_to_txt(input_dir)