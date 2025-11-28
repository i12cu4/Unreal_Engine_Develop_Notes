import re
import os

def extract_baidu_links_and_codes(file_path):
    """
    从文本文件中提取百度云链接和提取码
    
    :param file_path: 文本文件路径
    :return: 包含链接和提取码的字典列表
    """
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # 匹配百度云链接
            link_pattern = r'https?://pan\.baidu\.com/s/\S+'
            links = re.findall(link_pattern, content)
            
            # 匹配提取码 (支持多种格式)
            code_patterns = [
                r'提取码[：:\s]*(\w{4})',  # 提取码：abcd
                r'密码[：:\s]*(\w{4})',    # 密码：abcd
                r'提取码\s*[:：]?\s*(\w{4})',  # 提取码:abcd
                r'密码\s*[:：]?\s*(\w{4})',    # 密码:abcd
                r'提取码\s*[:：]?\s*(\w{4})\s', # 提取码: abcd
                r'密码\s*[:：]?\s*(\w{4})\s',   # 密码: abcd
                r'提取码[：:\s]*(\w{4})\s',     # 提取码：abcd
                r'密码[：:\s]*(\w{4})\s',       # 密码：abcd
            ]
            
            codes = []
            for pattern in code_patterns:
                found_codes = re.findall(pattern, content)
                codes.extend(found_codes)
            
            # 尝试找到每个链接对应的提取码
            lines = content.split('\n')
            for i, line in enumerate(lines):
                # 查找链接
                link_matches = re.findall(link_pattern, line)
                if not link_matches:
                    continue
                    
                link = link_matches[0]
                
                # 检查链接是否已经包含提取码
                if 'pwd=' in link:
                    # 如果链接已经包含提取码，则直接使用原链接
                    results.append({
                        'link': link,
                        'code': '已包含在链接中',
                        'combined': link
                    })
                    continue
                
                # 在当前行查找提取码
                code = None
                for pattern in code_patterns:
                    code_match = re.search(pattern, line)
                    if code_match:
                        code = code_match.group(1)
                        break
                
                # 如果当前行没有，尝试在后续几行中查找
                if not code:
                    for j in range(i+1, min(i+5, len(lines))):  # 最多查看后面4行
                        for pattern in code_patterns:
                            code_match = re.search(pattern, lines[j])
                            if code_match:
                                code = code_match.group(1)
                                break
                        if code:
                            break
                
                # 如果找到提取码，添加到结果中
                if code:
                    # 检查链接是否已经有查询参数
                    if '?' in link:
                        combined_link = f"{link}&pwd={code}"
                    else:
                        combined_link = f"{link}?pwd={code}"
                    
                    results.append({
                        'link': link,
                        'code': code,
                        'combined': combined_link
                    })
                else:
                    results.append({
                        'link': link,
                        'code': None,
                        'combined': link  # 没有提取码，只保存链接
                    })
                    
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return []
    
    return results

def save_combined_links(results, output_path):
    """
    将组合后的链接保存到文件
    
    :param results: 提取结果列表
    :param output_path: 输出文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            for result in results:
                file.write(result['combined'] + '\n')
        
        print(f"成功保存 {len(results)} 个链接到: {output_path}")
        
        # 打印统计信息
        with_code = sum(1 for r in results if r['code'] and r['code'] != '已包含在链接中')
        already_has_code = sum(1 for r in results if r['code'] == '已包含在链接中')
        without_code = len(results) - with_code - already_has_code
        
        print(f"统计结果:")
        print(f"- {with_code} 个链接添加了提取码")
        print(f"- {already_has_code} 个链接已包含提取码")
        print(f"- {without_code} 个链接没有找到提取码")
        
    except Exception as e:
        print(f"保存文件时出错: {e}")

def main():
    """
    主函数
    """
    # 获取输入文件路径
    input_path = input("请输入包含百度云链接的txt文件路径: ").strip()
    
    if not os.path.isfile(input_path):
        print("文件不存在，请检查路径")
        return
    
    # 获取输出文件路径
    output_path = input("请输入保存结果的txt文件路径(默认为原文件名+baidu_links.txt): ").strip()
    
    if not output_path:
        # 获取输入文件的目录和完整文件名（包含扩展名）
        input_dir = os.path.dirname(input_path)
        input_filename = os.path.basename(input_path)
        
        # 生成新的输出文件名：原文件名（包含扩展名）+ "baidu_links.txt"
        new_filename = f"{input_filename}baidu_links.txt"
        output_path = os.path.join(input_dir, new_filename)
    elif os.path.isdir(output_path):
        # 如果用户输入的是目录，同样使用原完整文件名生成新文件名
        input_filename = os.path.basename(input_path)
        new_filename = f"{input_filename}baidu_links.txt"
        output_path = os.path.join(output_path, new_filename)
    
    # 提取链接和提取码
    print("正在提取百度云链接和提取码...")
    results = extract_baidu_links_and_codes(input_path)
    
    if not results:
        print("未找到任何百度云链接")
        return
    
    print(f"找到 {len(results)} 个百度云链接")
    
    # 保存组合后的链接
    save_combined_links(results, output_path)

if __name__ == "__main__":
    main()