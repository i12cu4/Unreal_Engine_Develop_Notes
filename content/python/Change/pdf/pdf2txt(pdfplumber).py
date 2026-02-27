# 排版更好些
import os
import pdfplumber

def convert_pdf_to_txt(pdf_path, txt_path):
    """将单个PDF文件转换为TXT文件"""
    try:
        with pdfplumber.open(pdf_path) as pdf, open(txt_path, 'w', encoding='utf-8') as txt_file:
            for page_num, page in enumerate(pdf.pages):
                # 提取文本并添加页码标记
                text = page.extract_text()
                if text:
                    # txt_file.write(f"--- 第 {page_num + 1} 页 ---\n")
                    txt_file.write(text + "\n\n")
        return True, None
    except Exception as e:
        return False, str(e)

def batch_convert_pdf_to_txt(folder_path):
    """批量转换文件夹中的所有PDF文件"""
    # 统计变量
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    # 遍历文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                # 生成对应的TXT文件名
                txt_file = os.path.splitext(file)[0] + '.txt'
                txt_path = os.path.join(root, txt_file)
                
                # 检查是否已存在同名TXT文件
                if os.path.exists(txt_path):
                    print(f"跳过: {file} (已存在对应的TXT文件)")
                    skip_count += 1
                    continue
                
                print(f"转换中: {file}...", end='', flush=True)
                success, error = convert_pdf_to_txt(pdf_path, txt_path)
                
                if success:
                    print("成功")
                    success_count += 1
                else:
                    print(f"失败: {error}")
                    fail_count += 1
    
    # 打印汇总报告
    print("\n转换完成! 结果汇总:")
    print(f"✓ 成功转换: {success_count} 个文件")
    print(f"✗ 转换失败: {fail_count} 个文件")
    print(f"↺ 跳过文件: {skip_count} 个 (已存在TXT)")
    print(f"总处理文件: {success_count + fail_count + skip_count} 个")

if __name__ == "__main__":
    # 获取用户输入路径
    folder_path = r"C:\Users\chru\Desktop\托卡马克之冠\01答案备份"
    
    # 验证路径是否存在
    if not os.path.isdir(folder_path):
        print(f"错误: 路径 '{folder_path}' 不存在或不是文件夹")
    else:
        print(f"开始处理文件夹: {folder_path}")
        batch_convert_pdf_to_txt(folder_path)