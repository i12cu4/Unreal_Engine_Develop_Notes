import os
import pytesseract
from PIL import Image
from glob import glob

# ================= 用户配置区域 =================
# 设置Tesseract路径（根据您的安装位置）
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows默认路径
# TESSERACT_PATH = "/usr/bin/tesseract"  # Linux/Mac路径

# 设置输入目录
JPEG_DIR = r"C:\Users\chru\Desktop\123"

# 设置输出目录
HTML_DIR = JPEG_DIR
OUTPUT_FILE = os.path.join(HTML_DIR, "extracted_text.md")
# ===============================================

# 配置Tesseract路径
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text_from_image(image_path):
    """从图片中提取文本"""
    img = Image.open(image_path)
    # 中英文识别
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    return text.strip()

def process_images():
    """处理指定目录下的所有图片"""
    # 确保输出目录存在
    if not os.path.exists(HTML_DIR):
        os.makedirs(HTML_DIR)
        print(f"已创建输出目录: {HTML_DIR}")
    
    # 获取所有图片文件
    image_files = (
        glob(os.path.join(JPEG_DIR, '*.jpg')) + 
        glob(os.path.join(JPEG_DIR, '*.jpeg')) + 
        glob(os.path.join(JPEG_DIR, '*.JPG')) + 
        glob(os.path.join(JPEG_DIR, '*.JPEG'))
    )
    
    if not image_files:
        print(f"在目录 {JPEG_DIR} 中未找到任何JPG/JPEG图片")
        return
    
    md_content = f"# 图片文本提取结果\n\n> 源目录: `{JPEG_DIR}`\n\n"
    
    for idx, img_path in enumerate(image_files, 1):
        try:
            filename = os.path.basename(img_path)
            print(f"处理中 ({idx}/{len(image_files)}): {filename}")
            text = extract_text_from_image(img_path)
            
            # 使用绝对路径引用图片
            md_content += f"## 图片 {idx}: {filename}\n"
            md_content += f"![]({img_path})\n\n"  # 使用绝对路径确保图片可访问
            md_content += "```\n" + text + "\n```\n\n"
            md_content += "---\n\n"  # 分隔线
            
        except Exception as e:
            print(f"处理 {img_path} 时出错: {str(e)}")
    
    # 保存Markdown文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as md_file:
        md_file.write(md_content)
    
    print(f"完成! 结果已保存到 {OUTPUT_FILE}")

if __name__ == "__main__":
    # 检查输入目录是否存在
    if not os.path.exists(JPEG_DIR):
        print(f"错误: 输入目录不存在 - {JPEG_DIR}")
    else:
        process_images()