def find_unique_urls(file_a, file_b, output_file=None):
    """
    找出A文件中有哪些网址是B文件所没有的
    
    参数:
        file_a: A文本文件路径
        file_b: B文本文件路径
        output_file: 可选，输出结果的文件路径
    """
    # 读取A文件的所有网址
    with open(file_a, 'r', encoding='utf-8') as f:
        urls_a = set(line.strip() for line in f if line.strip())
    
    # 读取B文件的所有网址
    with open(file_b, 'r', encoding='utf-8') as f:
        urls_b = set(line.strip() for line in f if line.strip())
    
    # 找出A中有但B中没有的网址
    unique_urls = urls_a - urls_b
    
    # 输出结果
    print(f"A文件总共有 {len(urls_a)} 个网址")
    print(f"B文件总共有 {len(urls_b)} 个网址")
    print(f"A文件中独有的网址有 {len(unique_urls)} 个\n")
    
    if unique_urls:
        print("A文件中独有的网址:")
        for url in sorted(unique_urls):
            print(url)
    else:
        print("A文件中没有独有的网址，所有网址B文件都有")
    
    # 如果指定了输出文件，保存结果
    if output_file and unique_urls:
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in sorted(unique_urls):
                f.write(url + '\n')
        print(f"\n结果已保存到: {output_file}")
    
    return unique_urls


# 使用示例
if __name__ == "__main__":
    # 替换为你的实际文件路径
    file_a = r"D:\0code\LU\githubs\spider\TaskCompare\阿甘探AI_githubLib"
    file_b = r"D:\0code\LU\githubs\spider\TaskCompare\github_stars_i12cu4_all_api.txt"
    output_file = "None"  # 可选，不保存则设为None
    
    find_unique_urls(file_a, file_b, output_file)