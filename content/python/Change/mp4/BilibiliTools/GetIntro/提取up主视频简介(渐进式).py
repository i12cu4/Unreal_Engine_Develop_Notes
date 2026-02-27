import requests
import json
import time
import random
import os
from urllib.parse import urlparse, parse_qs

def get_videos_by_page(mid, page_num, page_size=30):
    """
    获取UP主指定页面的视频列表
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'https://space.bilibili.com/{mid}/'
    }
    
    url = f"https://api.bilibili.com/x/space/arc/search?mid={mid}&ps={page_size}&pn={page_num}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data['code'] != 0:
            print(f"第 {page_num} 页请求失败: {data.get('message', '未知错误')}")
            return None, False
            
        vlist = data['data']['list']['vlist']
        total_videos = data['data']['page']['count']
        has_more = page_num * page_size < total_videos
        
        return vlist, total_videos, has_more
        
    except Exception as e:
        print(f"获取第 {page_num} 页视频时出错: {e}")
        return None, 0, False

def get_video_description(bvid, max_retries=2):
    """
    获取单个视频的详细信息，包括简介（包含重试机制）
    """
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'https://www.bilibili.com/video/{bvid}'
    }
    
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(1, 2))
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 0:
                return data['data']['desc']
            else:
                print(f"获取视频{bvid}详情失败: {data['message']}")
                return None
                
        except Exception as e:
            print(f"获取视频{bvid}简介时出错 (第 {attempt+1} 次尝试): {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
                
    return None

def write_video_info_to_file(file_handle, video, description, is_last=False):
    """
    将单个视频信息写入文件
    """
    title = video['title']
    bvid = video['bvid']
    pub_date = time.strftime("%Y-%m-%d", time.localtime(video['created']))
    
    # 写入视频信息
    file_handle.write(f"【视频标题】: {title}\n")
    file_handle.write(f"【发布时间】: {pub_date}\n")
    file_handle.write(f"【视频BV号】: {bvid}\n")
    file_handle.write(f"【视频简介】: {description}\n")
    
    # 添加分隔符（最后一个视频不添加）
    if not is_last:
        file_handle.write("-" * 80 + "\n\n")
    
    # 刷新缓冲区，确保内容写入磁盘
    file_handle.flush()
    os.fsync(file_handle.fileno())

def process_videos_page_by_page(mid, output_file):
    """
    逐页处理视频，每获取一页就处理一页
    """
    page_num = 1
    page_size = 30
    total_videos = 0
    processed_count = 0
    success_count = 0
    
    # 创建文件并写入头部信息
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"UP主MID: {mid}\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.flush()
        os.fsync(f.fileno())
    
    print(f"开始逐页获取UP主(mid={mid})的视频...")
    
    while True:
        # 获取当前页的视频列表
        print(f"\n正在获取第 {page_num} 页视频...")
        result = get_videos_by_page(mid, page_num, page_size)
        
        if result[0] is None:
            print(f"第 {page_num} 页获取失败，等待后重试...")
            time.sleep(10)  # 等待10秒后重试
            continue
            
        videos, total, has_more = result
        
        # 如果是第一页，更新总视频数
        if page_num == 1:
            total_videos = total
            print(f"UP主共有 {total_videos} 个视频")
            
            # 更新文件头部的总视频数信息
            with open(output_file, 'r+', encoding='utf-8') as f:
                content = f.read()
                f.seek(0)
                f.write(f"UP主MID: {mid}\n")
                f.write(f"视频总数: {total_videos}\n")
                f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.write(content.split("=" * 80 + "\n\n", 1)[1] if "=" * 80 + "\n\n" in content else "")
                f.flush()
                os.fsync(f.fileno())
        
        if not videos:
            print("没有更多视频了")
            break
            
        print(f"成功获取第 {page_num} 页，共 {len(videos)} 个视频")
        
        # 处理当前页的所有视频
        for i, video in enumerate(videos, 1):
            title = video['title']
            bvid = video['bvid']
            processed_count += 1
            
            print(f"正在处理第 {page_num} 页第 {i} 个视频 ({processed_count}/{total_videos}): {title}")
            
            description = get_video_description(bvid)
            if description is None:
                description = "获取简介失败"
            else:
                success_count += 1
            
            # 计算是否是最后一个视频
            is_last = (processed_count == total_videos) and (i == len(videos)) and (not has_more)
            
            # 以追加模式打开文件，写入当前视频信息
            with open(output_file, 'a', encoding='utf-8') as f:
                write_video_info_to_file(f, video, description, is_last=is_last)
            
            # 单个视频处理完成后的小延迟
            time.sleep(random.uniform(0.5, 1.5))
        
        print(f"第 {page_num} 页处理完成，累计成功: {success_count}/{processed_count}")
        
        # 检查是否还有更多页面
        if not has_more:
            print("已处理所有页面")
            break
            
        page_num += 1
        
        # 页面之间的延迟，避免请求过快
        delay = random.uniform(3, 8)
        print(f"等待 {delay:.1f} 秒后获取下一页...")
        time.sleep(delay)
    
    return processed_count, success_count

def main():
    """主函数"""
    # 用户输入
    up_url = input("请输入B站UP主的播放全部页面URL: ").strip()
    
    # 从URL中提取mid
    mid = None
    try:
        parsed_url = urlparse(up_url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        for part in path_parts:
            if part.isdigit():
                mid = part
                break
    except:
        pass
        
    if not mid:
        print("无法从URL提取UP主ID，请手动输入UP主MID:")
        mid = input("请输入UP主MID: ").strip()
    
    # 保存文件
    save_path = input("请输入保存简介的txt文件路径(默认为当前目录): ").strip()
    if not save_path:
        save_path = os.getcwd()
    
    if os.path.isfile(save_path):
        save_dir = os.path.dirname(save_path)
    else:
        save_dir = save_path
    
    output_file = os.path.join(save_dir, f"b站up主_{mid}_视频简介.txt")
    
    # 逐页处理视频
    processed_count, success_count = process_videos_page_by_page(mid, output_file)
    
    print(f"\n处理完成！成功获取 {success_count}/{processed_count} 个视频的简介")
    print(f"所有视频简介已保存到: {output_file}")

if __name__ == "__main__":
    main()