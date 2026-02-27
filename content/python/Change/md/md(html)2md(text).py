import re
import argparse
import sys
from pathlib import Path

def remove_html_and_css(content):
    """
    从文本内容中移除HTML标签和CSS样式
    """
    # 移除CSS样式块
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    
    # 移除HTML注释
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # 移除所有HTML标签但保留内容
    content = re.sub(r'<[^>]+>', '', content)
    
    # 移除内联样式属性（如果存在）
    content = re.sub(r'\s*style\s*=\s*"[^"]*"', '', content)
    content = re.sub(r"\s*style\s*=\s*'[^']*'", '', content)
    
    # 移除可能残留的CSS选择器（如果存在）
    content = re.sub(r'#[a-zA-Z0-9_-]+\s*{', '', content)
    content = re.sub(r'\.[a-zA-Z0-9_-]+\s*{', '', content)
    
    # 移除多余的空白行
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    return content.strip()

def process_file(input_file, output_file=None):
    """
    处理单个文件
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return False
    
    cleaned_content = remove_html_and_css(content)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"已处理: {input_file} -> {output_file}")
        except Exception as e:
            print(f"写入文件时出错: {e}")
            return False
    else:
        # 如果没有指定输出文件，则打印到控制台
        print(cleaned_content)
    
    return True

def main():
    # 使用变量形式存储文件路径
    input_file_path = r"C:\Users\chru\Desktop\Unreal_Engine_Develop_Notes\README.md"  # 修改为你的输入文件路径
    output_file_path = r"C:\Users\chru\Desktop\Unreal_Engine_Develop_Notes\README2.md"  # 修改为你的输出文件路径，设为None则不保存文件
    
    # 检查输入文件是否存在
    input_path = Path(input_file_path)
    if not input_path.exists():
        print(f"错误: 文件 '{input_file_path}' 不存在")
        sys.exit(1)
    
    # 检查输出文件是否已存在（如果指定了输出路径）
    if output_file_path and Path(output_file_path).exists():
        response = input(f"文件 '{output_file_path}' 已存在，是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("操作已取消")
            sys.exit(0)
    
    # 处理文件
    success = process_file(input_file_path, output_file_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()