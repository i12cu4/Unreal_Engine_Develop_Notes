import requests
import json
import time
import random
import os
from urllib.parse import urlparse, parse_qs

def get_all_videos(mid, page_size=30, max_retries=300, delay_range=(3,8)):
    """
    获取UP主所有视频列表（支持分页，包含重试机制和延迟）
    
    :param mid: UP主UID
    :param page_size: 每页数量
    :param max_retries: 最大重试次数
    :param delay_range: 请求延迟范围（秒）
    :return: 视频列表
    """
    all_videos = []
    page_num = 1
    total_videos = 0
    has_more = True
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'https://space.bilibili.com/{mid}/'
    }
    
    while has_more:
        retries = 0
        while retries <= max_retries:
            try:
                # 添加随机延迟，避免请求过快
                time.sleep(random.uniform(delay_range[0], delay_range[1]))
                
                url = f"https://api.bilibili.com/x/space/arc/search?mid={mid}&ps={page_size}&pn={page_num}"
                print(f"正在请求第 {page_num} 页...")
                
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()  # 检查HTTP错误
                data = response.json()
                
                if data['code'] != 0:
                    error_msg = data.get('message', '未知错误')
                    # 检查是否是频率限制错误码
                    if data['code'] == -799 or "频繁" in error_msg:
                        print(f"第 {page_num} 页请求频繁，等待后重试...")
                        time.sleep(10)  # 等待更长时间
                        retries += 1
                        continue
                    else:
                        print(f"API请求失败 (页码 {page_num}): {error_msg}")
                        break
                
                # 获取视频列表
                vlist = data['data']['list']['vlist']
                if not vlist:
                    has_more = False
                    break
                
                # 首次请求时获取总视频数
                if page_num == 1:
                    total_videos = data['data']['page']['count']
                    print(f"UP主共有 {total_videos} 个视频")
                
                all_videos.extend(vlist)
                print(f"成功获取第 {page_num} 页，共 {len(vlist)} 个视频，累计 {len(all_videos)}/{total_videos}")
                
                # 检查是否已获取所有视频
                if len(all_videos) >= total_videos:
                    print("已获取所有视频列表")
                    has_more = False
                    break
                    
                page_num += 1
                break  # 跳出重试循环，继续下一页
                
            except requests.exceptions.RequestException as e:
                print(f"网络请求异常 (第 {retries+1} 次重试): {e}")
                retries += 1
                if retries <= max_retries:
                    wait_time = 5 * retries  # 重试等待时间递增
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                retries += 1
                if retries <= max_retries:
                    time.sleep(5)
            except Exception as e:
                print(f"获取第 {page_num} 页视频时出错: {e}")
                retries += 1
                if retries <= max_retries:
                    time.sleep(5)
        
        if retries > max_retries:
            print(f"第 {page_num} 页请求失败次数过多，停止获取")
            break
            
    return all_videos

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
            time.sleep(random.uniform(1, 2))  # 单个视频请求也添加延迟
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
                time.sleep(3)  # 重试前等待
                
    return None

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
    
    print(f"正在获取UP主(mid={mid})的所有视频，请耐心等待...")
    
    # 获取所有视频 - 增加延迟范围
    videos = get_all_videos(mid, delay_range=(2, 5))  # 增加请求间隔
    if not videos:
        print("未找到任何视频或获取视频列表失败")
        return
    
    print(f"成功获取 {len(videos)} 个视频，开始获取视频简介...")
    
    # 保存文件
    save_path = input("请输入保存简介的txt文件路径(默认为当前目录): ").strip()
    if not save_path:
        save_path = os.getcwd()
    
    if os.path.isfile(save_path):
        save_dir = os.path.dirname(save_path)
    else:
        save_dir = save_path
    
    output_file = os.path.join(save_dir, f"b站up主_{mid}_视频简介.txt")
    
    success_count = 0
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"UP主MID: {mid}\n")
        f.write(f"视频总数: {len(videos)}\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, video in enumerate(videos, 1):
            title = video['title']
            bvid = video['bvid']
            pub_date = time.strftime("%Y-%m-%d", time.localtime(video['created']))
            
            print(f"正在处理第 {i}/{len(videos)} 个视频: {title}")
            
            description = get_video_description(bvid)
            if description is None:
                description = "获取简介失败"
            else:
                success_count += 1
            
            # 写入文件
            f.write(f"【视频标题】: {title}\n")
            f.write(f"【发布时间】: {pub_date}\n")
            f.write(f"【视频BV号】: {bvid}\n")
            f.write(f"【视频简介】: {description}\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"处理完成！成功获取 {success_count}/{len(videos)} 个视频的简介")
    print(f"所有视频简介已保存到: {output_file}")

if __name__ == "__main__":
    main()