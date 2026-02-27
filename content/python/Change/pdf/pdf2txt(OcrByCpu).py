import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE" #bug:
import fnmatch
import datetime
import fitz  # PyMuPDF
from PIL import Image
import easyocr
import shutil
import time

#启动时间
start_time=time.time()
current_time=time.time()

#获取根目录的pdf名单
def get_pdf_files(path):
    # 确保路径存在
    if not os.path.exists(path):
        raise ValueError(f"{path} 不存在")
    # 使用os.walk获取路径下的所有文件
    for root, dirs, files in os.walk(path):
        # 使用fnmatch来匹配PDF文件
        pdf_files = fnmatch.filter(files, '*.pdf')
        # 返回PDF文件名
        return pdf_files

#将pdf分割切片成png
def pdf_to_images_and_save(pdf_path, output_folder,dpi):
    # 创建新文件夹
    os.makedirs(output_folder, exist_ok=True)
    # 打开 PDF 文件
    pdf_document = fitz.open(pdf_path)
    # 遍历每一页
    for page_number in range(pdf_document.page_count):
        # 获取页面对象
        page = pdf_document[page_number]
        # 获取页面的图像
        zoom_x=dpi
        zoom_y=dpi
        mat=fitz.Matrix(zoom_x,zoom_y)
        image_list = page.get_pixmap(matrix=mat)
        # 将 Pixmap 转换为 PIL Image
        image = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)
        # 保存图像为 PNG 文件
        image_path = os.path.join(output_folder, f"{page_number + 1}.png")
        image.save(image_path, "PNG")

#保存文件
def save_current_time_to_txt(path,filename):
    # 获取当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # 拼接文件名
    file_name = f"{current_time}.txt"
    # 指定路径
    temp_file_name= filename.rsplit('.',1)[0]+'_'+file_name
    full_path = os.path.join(path,temp_file_name)
    # 确保路径存在
    if not os.path.exists(path):
        raise ValueError(f"{path} 不存在")
    # 创建文件并写入当前时间
    with open(full_path, 'w', encoding='utf-8') as file:
        file.write(f"{filename}")
    return full_path
    
#easyOCR识别png
def process_png_directory(png_folder, txt_filename):
    global current_time
    # 初始化 EasyOCR
    reader = easyocr.Reader(['ch_sim','en'], gpu=True)# 默认语言设置为中文，根据需要可以更改
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
            
#删除文件夹
def DeleteDir(folder_path):
    # 检查文件夹是否存在
    if os.path.exists(folder_path):
        # 删除文件夹
        shutil.rmtree(folder_path)
        
path = "C:/Users/chru/ocr/"
#获取pdf名单
pdf_files = get_pdf_files(path)
print(f'pdf lists:{pdf_files}')

for pdf_name in pdf_files:
    global current_time
    pdf_path = os.path.join(path,pdf_name)
    file_name=pdf_name.split('.',1)[0]
    dir_path = os.path.join(path,file_name)
    #分割pdf为png
    pdf_to_images_and_save(pdf_path,dir_path,8.0)
    end_time=time.time()
    total_time=end_time-current_time
    current_time=end_time
    print(f'{file_name}文件夹分割用时{total_time}秒')
    #保存txt
    text_name=save_current_time_to_txt(path,file_name)    
    #EasyOCR识别并写入txt
    process_png_directory(dir_path, text_name)
    end_time=time.time()
    total_time=end_time-current_time
    current_time=end_time
    print(f'{file_name}文件识别用时{total_time}秒')
    #删除png的文件夹
    DeleteDir(dir_path)
    print(f'{file_name} 识别完成')

end_time=time.time()
print(f'全部完成 总用时{end_time-start_time}秒')