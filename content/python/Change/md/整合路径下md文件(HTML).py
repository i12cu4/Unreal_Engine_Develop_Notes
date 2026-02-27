import os
import argparse

def merge_md_files(input_dir, output_file):
    # 收集所有md文件的信息（文件名，路径）
    md_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.md'):
                file_path = os.path.join(root, file)
                md_files.append((file, file_path))
    
    # 按文件名排序
    md_files.sort(key=lambda x: x[0])
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for filename, filepath in md_files:
            with open(filepath, 'r', encoding='utf-8') as in_f:
                content = in_f.read()
            # 按格式写入文件名和内容
            out_f.write(f"<details>\n<summary>{filename}</summary>\n<pre><code>\n{content}\n</code></pre>\n</details>\n\n\n\n\n")

if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser(description='合并指定目录下的所有Markdown文件')
    parser.add_argument('input_dir', help='输入目录路径')
    parser.add_argument('output_file', help='输出文件路径')
    args = parser.parse_args()
    merge_md_files(args.input_dir, args.output_file)
    """
    merge_md_files(r"C:\Users\chru\Desktop\node", r"C:\Users\chru\Desktop\node\data2.md")