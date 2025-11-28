import requests
import re
import json
import time
import os
from urllib.parse import urlparse, parse_qs

class BilibiliSeriesCrawlerProgressive:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.output_file = None
    
    def extract_bvid(self, url):
        """从URL中提取BV号"""
        bv_pattern = r'BV[0-9A-Za-z]{10}'
        match = re.search(bv_pattern, url)
        return match.group() if match else None
    
    def get_mid_and_season_id(self, url):
        """从视频页面获取UP主ID和合集ID"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            html_content = response.text
            
            # 提取UP主ID (mid)
            mid_pattern = r'"mid":(\d+)'
            mid_match = re.search(mid_pattern, html_content)
            mid = mid_match.group(1) if mid_match else None
            
            # 提取合集ID (season_id)
            season_pattern = r'"season_id":(\d+)'
            season_match = re.search(season_pattern, html_content)
            season_id = season_match.group(1) if season_match else None
            
            return mid, season_id
            
        except Exception as e:
            print(f"获取页面信息失败: {e}")
            return None, None
    
    def get_series_videos_basic(self, mid, season_id):
        """获取合集中所有视频的基本信息（不包含详细简介）"""
        series_url = "https://api.bilibili.com/x/polymer/web-space/seasons_archives_list"
        params = {
            'mid': mid,
            'season_id': season_id,
            'sort_reverse': 'false',
            'page_num': 1,
            'page_size': 100
        }
        
        try:
            response = self.session.get(series_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] != 0:
                print(f"获取合集信息失败: {data['message']}")
                return []
            
            videos = []
            for item in data['data']['archives']:
                video_info = {
                    'title': item.get('title', ''),
                    'publish_time': time.strftime("%Y-%m-%d", time.localtime(item.get('pubdate', 0))),
                    'bvid': item.get('bvid', ''),
                    'description': ''  # 初始化为空，后续单独获取
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"请求合集信息失败: {e}")
            return []
    
    def get_video_detail(self, bvid):
        """获取单个视频的详细信息，包括简介"""
        try:
            # 使用B站API获取视频详细信息
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            response = self.session.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 0:
                video_data = data['data']
                return {
                    'title': video_data.get('title', ''),
                    'publish_time': time.strftime("%Y-%m-%d", time.localtime(video_data.get('pubdate', 0))),
                    'bvid': video_data.get('bvid', ''),
                    'description': video_data.get('desc', '')
                }
            else:
                print(f"获取视频{bvid}详情失败: {data['message']}")
                return None
                
        except Exception as e:
            print(f"请求视频详情失败: {e}")
            return None
    
    def initialize_output_file(self, mid, total_videos):
        """初始化输出文件并写入头部信息"""
        filename = f"b站up主_{mid}_视频简介.txt"
        self.output_file = filename
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"UP主MID: {mid}\n")
            f.write(f"视频总数: {total_videos}\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.flush()
            os.fsync(f.fileno())
        
        print(f"输出文件已创建: {filename}")
        return filename
    
    def write_video_info(self, video, index, total, is_last=False):
        """将单个视频信息写入文件"""
        if not self.output_file:
            return
        
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"【视频标题】: {video['title']}\n")
                f.write(f"【发布时间】: {video['publish_time']}\n")
                f.write(f"【视频BV号】: {video['bvid']}\n")
                f.write(f"【视频简介】: {video['description']}\n")
                
                # 如果不是最后一个视频，添加分隔符
                if not is_last:
                    f.write("\n" + "=" * 50 + "\n\n")
                
                f.flush()
                os.fsync(f.fileno())
            
            print(f"[{index}/{total}] 已保存: {video['title']}")
            
        except Exception as e:
            print(f"写入文件失败: {e}")
    
    def crawl_progressive(self, url):
        """渐进式爬取函数 - 逐页获取并实时保存"""
        print("开始获取B站视频合集信息...")
        
        # 提取BV号
        bvid = self.extract_bvid(url)
        if not bvid:
            print("无法从URL中提取BV号")
            return
        
        print(f"获取到BV号: {bvid}")
        
        # 获取UP主ID和合集ID
        mid, season_id = self.get_mid_and_season_id(url)
        
        if not mid or not season_id:
            print("未找到合集信息，该视频可能不属于任何合集")
            return
        
        print(f"找到UP主ID: {mid}, 合集ID: {season_id}")
        
        # 获取合集视频基本信息
        videos_basic = self.get_series_videos_basic(mid, season_id)
        
        if not videos_basic:
            print("未获取到任何视频信息")
            return
        
        total_videos = len(videos_basic)
        print(f"成功获取到 {total_videos} 个视频的基本信息")
        
        # 初始化输出文件
        self.initialize_output_file(mid, total_videos)
        
        # 逐个获取视频详情并实时保存
        success_count = 0
        for i, video_basic in enumerate(videos_basic, 1):
            print(f"[{i}/{total_videos}] 正在获取视频详情: {video_basic['title']}")
            
            # 获取视频详情
            video_detail = self.get_video_detail(video_basic['bvid'])
            
            if video_detail:
                # 使用获取到的详情
                video_info = video_detail
                success_count += 1
            else:
                # 如果获取详情失败，使用基础信息
                video_info = video_basic
                print(f"  获取详情失败，使用基础信息")
            
            # 判断是否是最后一个视频
            is_last = (i == total_videos)
            
            # 写入文件
            self.write_video_info(video_info, i, total_videos, is_last)
            
            # 添加延迟，避免请求过快
            if i < total_videos:  # 最后一个视频不需要延迟
                time.sleep(0.5)
        
        print(f"\n处理完成! 成功获取 {success_count}/{total_videos} 个视频的详细信息")
        print(f"视频合集信息已保存到: {self.output_file}")
        
        # 打印部分内容预览
        if success_count > 0:
            print("\n前3个视频的预览:")
            # 重新读取文件获取前3个视频
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 分割视频块
                    blocks = content.split('=' * 50 + '\n\n')
                    # 跳过文件头
                    for i, block in enumerate(blocks[1:4], 1):  # 只取前3个
                        if block.strip():
                            title_match = re.search(r'【视频标题】: (.+)', block)
                            if title_match:
                                title = title_match.group(1)
                                desc_match = re.search(r'【视频简介】: (.+?)(?=\n|$)', block, re.DOTALL)
                                desc_preview = desc_match.group(1)[:50] + '...' if desc_match and len(desc_match.group(1)) > 50 else (desc_match.group(1) if desc_match else '')
                                print(f"视频{i}:")
                                print(f"  标题: {title}")
                                print(f"  简介: {desc_preview}")
            except Exception as e:
                print(f"读取预览失败: {e}")

def main():
    crawler = BilibiliSeriesCrawlerProgressive()
    
    # 从用户输入获取URL
    url = input("请输入B站视频URL: ").strip()
    
    if not url:
        print("URL不能为空")
        return
    
    crawler.crawl_progressive(url)

if __name__ == "__main__":
    main()