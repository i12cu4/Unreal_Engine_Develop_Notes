import requests
import re
import json
import time
from urllib.parse import urlparse, parse_qs

class BilibiliSeriesCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
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
    
    def get_series_videos(self, mid, season_id):
        """获取合集中所有视频信息"""
        # 使用B站API获取合集视频列表
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
                # 为每个视频单独获取详细信息，确保能获取到简介
                video_detail = self.get_video_detail(item['bvid'])
                if video_detail:
                    videos.append(video_detail)
                else:
                    # 如果获取详情失败，使用基础信息
                    video_info = self.format_video_info(item)
                    videos.append(video_info)
                
                # 添加延迟，避免请求过快
                time.sleep(0.5)
            
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
    
    def format_video_info(self, video_data):
        """格式化视频信息"""
        return {
            'title': video_data.get('title', ''),
            'publish_time': time.strftime("%Y-%m-%d", time.localtime(video_data.get('pubdate', 0))),
            'bvid': video_data.get('bvid', ''),
            'description': video_data.get('desc', '')
        }
    
    def crawl(self, url):
        """主爬取函数"""
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
        
        # 获取合集视频信息
        videos = self.get_series_videos(mid, season_id)
        
        if not videos:
            print("未获取到任何视频信息")
            return
        
        print(f"成功获取到 {len(videos)} 个视频信息")
        
        # 保存到文件
        self.save_to_file(videos, mid)
    
    def save_to_file(self, videos, mid):
        """保存视频信息到txt文件，文件名格式为：b站up主_{mid}_视频简介.txt"""
        filename = f"b站up主_{mid}_视频简介.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            for i, video in enumerate(videos, 1):
                f.write(f"【视频标题】: {video['title']}\n")
                f.write(f"【发布时间】: {video['publish_time']}\n")
                f.write(f"【视频BV号】: {video['bvid']}\n")
                f.write(f"【视频简介】: {video['description']}\n")
                
                # 如果不是最后一个视频，添加分隔符
                if i < len(videos):
                    f.write("\n" + "="*50 + "\n\n")
        
        print(f"视频合集信息已保存到: {filename}")
        
        # 打印部分内容预览
        print("\n前3个视频的预览:")
        for i, video in enumerate(videos[:3], 1):
            print(f"视频{i}:")
            print(f"  标题: {video['title']}")
            print(f"  简介: {video['description'][:50]}{'...' if len(video['description']) > 50 else ''}")

def main():
    crawler = BilibiliSeriesCrawler()
    
    # 从用户输入获取URL
    url = input("请输入B站视频URL: ").strip()
    
    if not url:
        print("URL不能为空")
        return
    
    crawler.crawl(url)

if __name__ == "__main__":
    main()