import re
import os
from urllib.parse import urlparse, parse_qs, urlencode

def complete_url(url):
    """
    补全不完整的网址，添加https://前缀
    """
    if url.startswith(('http://', 'https://')):
        return url
    
    common_domains = [
        'pan.baidu.com', 'pan.quark.cn', 'www.aliyundrive.com',
        'cloud.189.cn', 'yun.baidu.com', 'github.com', 'gitee.com',
        'pan.xunlei.com'  # 添加迅雷云盘
    ]
    
    for domain in common_domains:
        if url.startswith(domain):
            return f"https://{url}"
    
    if '.' in url and not url.startswith('http'):
        return f"https://{url}"
    
    return url

def add_password_to_url(url, password):
    """
    为网盘链接添加密码参数，特别是处理百度网盘链接
    返回处理后的URL和是否成功添加密码
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # 检查是否已经包含密码参数
        query_params = parse_qs(parsed_url.query)
        
        # 处理百度网盘链接
        if 'pan.baidu.com' in domain:
            # 如果URL中还没有pwd参数，则添加
            if 'pwd' not in query_params:
                # 确保密码不为空
                if password and password.strip():
                    query_params['pwd'] = password.strip()
                    new_query = urlencode(query_params, doseq=True)
                    new_url = parsed_url._replace(query=new_query).geturl()
                    return new_url, True
            # 如果已有pwd参数，检查是否需要更新（可选，根据需求）
            # 这里选择不更新已存在的参数
            return url, False
                
        elif 'pan.quark.cn' in domain:
            # 夸克网盘使用 pwd 参数
            if 'pwd' not in query_params:
                query_params['pwd'] = password
                new_query = urlencode(query_params, doseq=True)
                new_url = parsed_url._replace(query=new_query).geturl()
                return new_url, True
                
        elif 'pan.xunlei.com' in domain:
            # 迅雷云盘使用 code 参数
            if 'code' not in query_params:
                query_params['code'] = password
                new_query = urlencode(query_params, doseq=True)
                new_url = parsed_url._replace(query=new_query).geturl()
                return new_url, True
        
        # 如果不支持的平台或已经包含密码参数，返回原URL
        return url, False
        
    except Exception as e:
        print(f"处理URL密码参数时出错: {e}")
        return url, False

def extract_video_titles_and_urls(file_path):
    """
    从文本文件中提取视频标题和简介中包含网址的行，并合并提取码信息
    """
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 方法1: 使用正则表达式直接匹配所有视频块
        # 匹配模式: 【视频标题】: 标题内容 + 任意内容直到下一个【视频标题】或文件结束
        video_pattern = r'【视频标题】: (.+?)\n【发布时间】: (.+?)\n【视频BV号】: (.+?)\n【视频简介】: (.+?)(?=\n【视频标题】: |\Z)'
        matches = list(re.finditer(video_pattern, content, re.DOTALL))
        
        print(f"使用正则表达式找到 {len(matches)} 个视频")
        
        for match in matches:
            title = match.group(1).strip()
            description = match.group(4).strip()
            
            print(f"处理视频: {title}")
            
            # 提取包含网址的行和提取码信息
            url_lines = extract_url_lines_from_description(description)
            
            results.append({
                'title': title,
                'url_lines': url_lines
            })
        
        # 方法2: 如果方法1没有找到任何视频，尝试使用分隔符分割
        if not results:
            print("方法1未找到视频，尝试使用分隔符分割...")
            # 尝试多种可能的分隔符
            separators = [
                '-' * 80 + '\n\n',
                '=' * 50 + '\n\n',
                '-' * 80 + '\n',
                '=' * 50 + '\n',
                '\n\n',
            ]
            
            for separator in separators:
                if separator in content:
                    print(f"使用分隔符: {repr(separator)}")
                    blocks = content.split(separator)
                    # 跳过文件头
                    blocks = blocks[1:] if len(blocks) > 1 else blocks
                    
                    for block in blocks:
                        if not block.strip():
                            continue
                            
                        # 提取视频标题
                        title_match = re.search(r'【视频标题】: (.+)', block)
                        if not title_match:
                            continue
                            
                        title = title_match.group(1).strip()
                        
                        # 提取简介
                        desc_match = re.search(r'【视频简介】: (.+?)(?=\n【|$)', block, re.DOTALL)
                        if not desc_match:
                            results.append({'title': title, 'url_lines': []})
                            continue
                            
                        description = desc_match.group(1)
                        url_lines = extract_url_lines_from_description(description)
                        
                        results.append({
                            'title': title,
                            'url_lines': url_lines
                        })
                    
                    if results:
                        print(f"使用分隔符方法找到 {len(results)} 个视频")
                        break
        
        # 方法3: 如果以上方法都失败，尝试逐行解析
        if not results:
            print("尝试逐行解析...")
            lines = content.split('\n')
            current_video = None
            
            for line in lines:
                # 检测视频标题
                title_match = re.match(r'【视频标题】: (.+)', line)
                if title_match:
                    if current_video:
                        results.append(current_video)
                    
                    current_video = {
                        'title': title_match.group(1).strip(),
                        'url_lines': []
                    }
                    continue
                
                # 检测简介开始
                if current_video and line.startswith('【视频简介】: '):
                    description = line.replace('【视频简介】: ', '')
                    # 继续读取直到下一个标题或分隔符
                    continue
                
                # 如果在简介中，检查是否包含网址
                if current_video and current_video.get('in_description', False):
                    # 检查行中是否包含网址
                    url_pattern = r'(https?://[^\s]+)|([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/[^\s]*)'
                    url_match = re.search(url_pattern, line)
                    
                    if url_match:
                        # 提取网址部分
                        url = url_match.group(1) or url_match.group(2)
                        
                        # 补全网址
                        completed_url = complete_url(url)
                        
                        # 替换行中的网址为补全后的网址
                        line = line.replace(url, completed_url)
                        
                        current_video['url_lines'].append(line)
                
                # 检测简介结束和下一个标题开始
                if line.startswith('【视频标题】: ') and current_video:
                    current_video['in_description'] = False
            
            # 添加最后一个视频
            if current_video:
                results.append(current_video)
                
            print(f"逐行解析找到 {len(results)} 个视频")
                    
    except Exception as e:
        print(f"读取文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    return results

def extract_url_lines_from_description(description):
    """
    从简介文本中提取包含网址的行，并处理提取码信息
    """
    url_lines = []
    lines = description.split('\n')
    i = 0
    
    # 支持的网盘域名列表
    supported_pan_domains = ['pan.baidu.com', 'pan.quark.cn', 'pan.xunlei.com']
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # 检查行中是否包含网址
        url_pattern = r'(https?://[^\s]+)|([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/[^\s]*)'
        url_matches = re.findall(url_pattern, line)
        
        if url_matches:
            # 检查当前行是否包含支持的网盘链接
            has_supported_pan = False
            for url_match in url_matches:
                url = url_match[0] or url_match[1]
                completed_url = complete_url(url)
                if any(domain in completed_url for domain in supported_pan_domains):
                    has_supported_pan = True
                    break
            
            # 只有包含支持的网盘链接时才处理提取码
            extracted_password = None
            line_modified = False
            
            if has_supported_pan:
                # 在当前行直接搜索提取码
                current_line_codes = re.findall(r'提取码[:：]\s*(\w{4})', line)
                if current_line_codes:
                    extracted_password = current_line_codes[0]
                
                # 如果当前行没找到，再检查下一行
                if not extracted_password and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # 检查提取码模式
                    code_patterns = [
                        r'提取码[：:\s]*(\w{4})',
                        r'密码[：:\s]*(\w{4})',
                        r'提取码\s*[:：]?\s*(\w{4})',
                        r'密码\s*[:：]?\s*(\w{4})'
                    ]
                    
                    for pattern in code_patterns:
                        code_match = re.search(pattern, next_line)
                        if code_match:
                            extracted_password = code_match.group(1)
                            line_modified = True
                            i += 1  # 跳过下一行，因为它已经被处理
                            break
            
            # 处理行中的所有URL
            processed_line = line
            if line_modified:
                processed_line = f"{line}  提取码：{extracted_password}"
            
            # 对每个URL进行处理
            for url_match in url_matches:
                original_url = url_match[0] or url_match[1]
                completed_url = complete_url(original_url)
                
                # 只有支持的网盘链接且找到提取码时才添加密码参数
                if extracted_password and any(domain in completed_url for domain in supported_pan_domains):
                    enhanced_url, success = add_password_to_url(completed_url, extracted_password)
                    if success:
                        processed_line = processed_line.replace(original_url, enhanced_url)
                else:
                    # 对于非网盘链接或没有提取码的情况，只补全URL
                    processed_line = processed_line.replace(original_url, completed_url)
            
            url_lines.append(processed_line)
        i += 1
    
    return url_lines

def save_extracted_content(results, output_path):
    """
    将提取的内容保存到文件
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            for i, result in enumerate(results):
                # 写入标题
                file.write(result['title'] + '\n')
                
                # 写入包含网址的行
                for line in result['url_lines']:
                    file.write(line + '\n')
                
                # 如果不是最后一个结果，添加空行分隔
                if i < len(results) - 1:
                    file.write('\n')
        
        print(f"成功保存 {len(results)} 个视频的提取内容到: {output_path}")
        
        # 统计处理的网盘链接
        baidu_count = 0
        quark_count = 0
        xunlei_count = 0
        
        for result in results:
            for line in result['url_lines']:
                if 'pan.baidu.com' in line and 'pwd=' in line:
                    baidu_count += 1
                elif 'pan.quark.cn' in line and 'pwd=' in line:
                    quark_count += 1
                elif 'pan.xunlei.com' in line and 'code=' in line:
                    xunlei_count += 1
        
        # 打印统计信息
        total_urls = sum(len(result['url_lines']) for result in results)
        print(f"统计结果:")
        print(f"- 共处理 {len(results)} 个视频")
        print(f"- 共提取 {total_urls} 个包含网址的行")
        print(f"- 百度网盘增强链接: {baidu_count} 个")
        print(f"- 夸克网盘增强链接: {quark_count} 个")
        print(f"- 迅雷云盘增强链接: {xunlei_count} 个")
        
    except Exception as e:
        print(f"保存文件时出错: {e}")

def main():
    """
    主函数
    """
    # 获取输入文件路径
    input_path = input("请输入包含视频信息的txt文件路径: ").strip()
    
    if not os.path.isfile(input_path):
        print("文件不存在，请检查路径")
        return
    
    # 获取输出文件路径
    output_path = input("请输入保存结果的txt文件路径(默认为原文件名+extracted_urls.txt): ").strip()
    
    if not output_path:
        # 获取输入文件的目录和完整文件名（包含扩展名）
        input_dir = os.path.dirname(input_path)
        input_filename = os.path.basename(input_path)
        
        # 生成新的输出文件名：原文件名（包含扩展名）+ "extracted_urls.txt"
        new_filename = f"{input_filename}extracted_urls.txt"
        output_path = os.path.join(input_dir, new_filename)
    elif os.path.isdir(output_path):
        # 如果用户输入的是目录，同样使用原完整文件名生成新文件名
        input_filename = os.path.basename(input_path)
        new_filename = f"{input_filename}extracted_urls.txt"
        output_path = os.path.join(output_path, new_filename)
    
    # 提取视频标题和网址行
    print("正在提取视频标题和包含网址的行...")
    results = extract_video_titles_and_urls(input_path)
    
    if not results:
        print("未找到任何视频信息")
        return
    
    print(f"找到 {len(results)} 个视频信息")
    
    # 保存提取的内容
    save_extracted_content(results, output_path)
    
    # 显示预览
    print("\n前3个视频的预览:")
    for i, result in enumerate(results[:3], 1):
        print(f"视频{i}:")
        print(f"  标题: {result['title']}")
        print(f"  包含网址的行: {len(result['url_lines'])} 行")
        if result['url_lines']:
            for line in result['url_lines']:
                print(f"    - {line}")

if __name__ == "__main__":
    main()