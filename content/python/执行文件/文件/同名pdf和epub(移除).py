import os
import send2trash
from collections import defaultdict

def find_and_remove_duplicate_epubs(target_path):
    """
    查找同名但不同格式的PDF和EPUB文件，并将EPUB文件移动到回收站
    """
    # 存储文件名（不含扩展名）和对应的文件路径
    file_dict = defaultdict(list)
    
    # 支持的扩展名
    pdf_extensions = {'.pdf'}
    epub_extensions = {'.epub'}
    
    print(f"开始扫描路径: {target_path}")
    print("正在查找同名的PDF和EPUB文件...")
    
    # 遍历所有文件和文件夹
    for root, dirs, files in os.walk(target_path):
        for file in files:
            file_path = os.path.join(root, file)
            filename, extension = os.path.splitext(file)
            extension_lower = extension.lower()
            
            # 只处理PDF和EPUB文件
            if extension_lower in pdf_extensions or extension_lower in epub_extensions:
                file_dict[filename].append((file_path, extension_lower))
    
    # 查找有PDF和EPUB同名的文件
    epub_to_remove = []
    
    for filename, file_list in file_dict.items():
        has_pdf = any(ext == '.pdf' for _, ext in file_list)
        has_epub = any(ext == '.epub' for _, ext in file_list)
        
        # 如果同时存在PDF和EPUB，记录EPUB文件
        if has_pdf and has_epub:
            epub_files = [path for path, ext in file_list if ext == '.epub']
            pdf_files = [path for path, ext in file_list if ext == '.pdf']
            
            print(f"\n找到同名文件: {filename}")
            print(f"  PDF文件: {pdf_files}")
            print(f"  EPUB文件: {epub_files}")
            
            epub_to_remove.extend(epub_files)
    
    # 移动EPUB文件到回收站
    if epub_to_remove:
        print(f"\n共找到 {len(epub_to_remove)} 个EPUB文件与PDF文件同名")
        print("即将移动到回收站的EPUB文件:")
        for epub in epub_to_remove:
            print(f"  {epub}")
        
        confirm = input("\n是否要将这些EPUB文件移动到回收站？(y/n): ").lower()
        
        if confirm == 'y':
            for epub_file in epub_to_remove:
                try:
                    send2trash.send2trash(epub_file)
                    print(f"已移动到回收站: {epub_file}")
                except Exception as e:
                    print(f"移动失败 {epub_file}: {e}")
            print(f"\n操作完成! 已移动 {len(epub_to_remove)} 个EPUB文件到回收站")
        else:
            print("操作已取消")
    else:
        print("未找到同名的PDF和EPUB文件")

def main():
    # 获取用户指定的路径
    target_path = input("请输入要扫描的路径: ").strip()
    
    # 检查路径是否存在
    if not os.path.exists(target_path):
        print(f"错误: 路径 '{target_path}' 不存在")
        return
    
    # 检查路径是否是文件夹
    if not os.path.isdir(target_path):
        print(f"错误: '{target_path}' 不是文件夹")
        return
    
    find_and_remove_duplicate_epubs(target_path)

if __name__ == "__main__":
    main()