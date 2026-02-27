import os
import pytesseract
import cv2
import numpy as np
from PIL import Image
import unicodedata
import shutil
import re
import sys

# 设置Tesseract路径 - 保持您提供的路径不变
pytesseract.pytesseract.tesseract_cmd = r'C:\Program File\Tesseract-OCR\tesseract.exe'

# 禁用OpenCV的日志输出 - 兼容不同版本的解决方案
try:
    # 尝试使用新版本的日志控制
    cv2.setLogLevel(cv2.LOG_LEVEL_ERROR)
except AttributeError:
    # 如果新版本方法不可用，使用旧版本方法
    cv2.setLogLevel(0)  # 0 = SILENT, 1 = ERROR, 2 = WARN, 3 = INFO, 4 = DEBUG

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
        # 1. 尝试使用OpenCV读取 - 添加cv2.IMREAD_UNCHANGED参数避免警告
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            # 如果是4通道图像（RGBA），转换为3通道（RGB）
            if len(img.shape) == 3 and img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
        
        # 2. 如果OpenCV失败，尝试使用PIL
        with Image.open(image_path) as pil_img:
            # 转换为RGB模式（如果是RGBA）
            if pil_img.mode == 'RGBA':
                pil_img = pil_img.convert('RGB')
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            return img
    except Exception as e:
        # 3. 作为最后手段，尝试复制文件并重命名
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
            img = cv2.imread(temp_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                # 如果是4通道图像，转换为3通道
                if len(img.shape) == 3 and img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                return img
                
            # 如果仍然失败，使用PIL
            with Image.open(temp_path) as pil_img:
                if pil_img.mode == 'RGBA':
                    pil_img = pil_img.convert('RGB')
                return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e2:
            # 获取详细的错误信息
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            error_details = f"{exc_type} in {fname} line {exc_tb.tb_lineno}: {str(e2)}"
            
            raise ValueError(f"无法读取图像: {os.path.basename(image_path)} - 原因: {error_details}")
        finally:
            # 清理临时文件
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    return None

def enhance_image_quality(img):
    """
    高级图像增强处理
    专注于提高汉字识别精度
    """
    # 1. 转换为灰度图
    if len(img.shape) == 3:  # 如果是彩色图像
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:  # 如果已经是灰度图
        gray = img
    
    # 2. 自适应直方图均衡化（增强对比度）
    try:
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16, 16))
        equalized = clahe.apply(gray)
    except:
        # 如果CLAHE失败，使用普通直方图均衡化
        equalized = cv2.equalizeHist(gray)
    
    # 3. 锐化处理 - 强化汉字笔画
    sharpen_kernel = np.array([[0, -1, 0],
                              [-1, 5, -1],
                              [0, -1, 0]])
    sharpened = cv2.filter2D(equalized, -1, sharpen_kernel)
    
    # 4. 去噪处理（保留边缘）
    denoised = cv2.bilateralFilter(sharpened, 9, 75, 75)
    
    # 5. 自适应阈值二值化
    try:
        binary = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 31, 10
        )
    except:
        # 如果自适应阈值失败，使用普通阈值
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary

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

def ocr_entire_image(img):
    """对整个图像进行OCR识别"""
    # OCR配置
    config = optimize_ocr_config()
    
    # 转换为PIL格式
    img_pil = Image.fromarray(img)
    
    # 尝试不同的识别策略
    results = []
    
    # 策略1: 标准识别
    try:
        text1 = pytesseract.image_to_string(
            img_pil, 
            lang='chi_sim',  # 仅中文
            config=config
        )
        results.append(text1)
    except Exception as e:
        print(f"标准OCR失败: {str(e)}")
        results.append("")
    
    # 策略2: 轻微旋转图像后识别
    for angle in [-1, 0, 1]:
        try:
            rotated = img_pil.rotate(angle, fillcolor=255)
            text = pytesseract.image_to_string(
                rotated, 
                lang='chi_sim',
                config=config
            )
            results.append(text)
        except:
            results.append("")
    
    # 选择汉字最多的结果
    best_text = ""
    max_hanzi = 0
    for text in results:
        hanzi_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        if hanzi_count > max_hanzi:
            max_hanzi = hanzi_count
            best_text = text
    
    return best_text

def process_image_file(image_path):
    """处理单个图像文件并保存结果"""
    try:
        print(f"\n{'='*50}")
        print(f"开始处理文件: {image_path}")
        
        # 1. 安全读取图像
        img = safe_read_image(image_path)
        if img is None:
            raise ValueError("无法读取图像文件")
            
        # 2. 图像增强
        enhanced_img = enhance_image_quality(img)
        
        # 3. OCR识别
        text = ocr_entire_image(enhanced_img)
        
        # 4. 后处理：移除多余空行
        cleaned_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        
        # 5. 构建输出路径
        dir_name = os.path.dirname(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(dir_name, f"{base_name}.txt")
        
        # 6. 保存结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        print(f"转换完成: {os.path.basename(image_path)}")
        print(f"字符数: {len(cleaned_text)}")
        print(f"输出位置: {output_path}")
        return True
    
    except Exception as e:
        print(f"\n处理文件 {image_path} 失败: {str(e)}")
        # 保存错误日志到原始目录
        log_path = os.path.join(os.path.dirname(image_path), "ocr_error_log.txt")
        with open(log_path, 'a', encoding='utf-8') as log:
            log.write(f"{image_path}: {str(e)}\n")
        return False

def convert_jpg_to_txt(root_dir):
    """
    递归转换目录及其子目录下的所有图像文件为TXT
    结果文件保存在原始图片所在目录
    """
    # 支持的图像文件扩展名
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    # 统计变量
    total_files = 0
    success_count = 0
    fail_count = 0
    
    # 递归遍历所有目录
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 跳过临时目录
        if "temp_ocr" in dirpath:
            continue
            
        # 处理当前目录中的图像文件
        for filename in filenames:
            if filename.lower().endswith(valid_extensions):
                total_files += 1
                image_path = os.path.join(dirpath, filename)
                if process_image_file(image_path):
                    success_count += 1
                else:
                    fail_count += 1
    
    if total_files == 0:
        print(f"在 {root_dir} 及其子目录中未找到图像文件")
        return
    
    print(f"\n{'='*50}")
    print(f"处理完成! 总文件数: {total_files}, 成功: {success_count}, 失败: {fail_count}")
    print(f"所有结果文件保存在原始图片所在目录")

if __name__ == "__main__":
    # 设置根目录
    root_dir = r"C:\Users\chru\Desktop\123"
    
    # 处理所有图像文件
    convert_jpg_to_txt(root_dir)