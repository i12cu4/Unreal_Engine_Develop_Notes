import os
import re
import requests
import json
import time
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

class BilibiliSeriesDownloaderProgressive:
    def __init__(self, save_path="./bilibili_videos"):
        """
        初始化下载器
        :param save_path: 视频保存路径
        """
        self.save_path = save_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        })
        
        # 创建保存目录
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        # 下载状态记录文件
        self.status_file = os.path.join(save_path, "download_status.json")
        self.download_status = self.load_download_status()

    def load_download_status(self):
        """加载下载状态"""
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_download_status(self):
        """保存下载状态"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存下载状态失败: {e}")

    def update_download_status(self, bvid, status, filename=None):
        """更新单个视频的下载状态"""
        self.download_status[bvid] = {
            'status': status,  # 'downloaded', 'skipped', 'failed'
            'filename': filename,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_download_status()

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
                    'bvid': item.get('bvid', ''),
                    'cid': item.get('cid', ''),
                    'pubdate': item.get('pubdate', 0)
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"请求合集信息失败: {e}")
            return []

    def sanitize_filename(self, filename):
        """清理文件名中的非法字符"""
        # 移除或替换文件名中的非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # 限制文件名长度，避免路径过长
        if len(filename) > 100:
            filename = filename[:100]
        return filename

    def get_video_play_url(self, bvid, cid):
        """获取视频播放URL"""
        try:
            # 获取视频下载链接
            play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=80&type=&otype=json"
            response = self.session.get(play_url)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] != 0:
                print(f"获取播放链接失败: {data.get('message', '未知错误')}")
                return None
            
            # 获取视频链接
            video_url = data['data']['durl'][0]['url']
            
            # 添加必要的headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': f'https://www.bilibili.com/video/{bvid}',
                'Range': 'bytes=0-'
            }
            
            return video_url, headers
            
        except Exception as e:
            print(f"获取视频播放URL失败: {e}")
            return None, None

    def check_video_exists(self, title):
        """检查视频是否已存在"""
        filename = f"{self.sanitize_filename(title)}.mp4"
        filepath = os.path.join(self.save_path, filename)
        
        # 检查文件是否存在
        if os.path.exists(filepath):
            return True, filename
        
        # 检查下载状态
        for bvid, status_info in self.download_status.items():
            if status_info.get('filename') == filename and status_info.get('status') == 'downloaded':
                return True, filename
        
        return False, filename

    def download_single_video(self, video_info, index, total):
        """下载单个视频"""
        try:
            title = video_info['title']
            bvid = video_info['bvid']
            cid = video_info['cid']
            
            print(f"[{index}/{total}] 开始处理: {title}")
            
            # 检查视频是否已存在
            exists, filename = self.check_video_exists(title)
            if exists:
                print(f"  视频已存在，跳过: {filename}")
                self.update_download_status(bvid, 'skipped', filename)
                return True
            
            # 获取视频播放URL
            result = self.get_video_play_url(bvid, cid)
            if not result:
                print(f"  获取视频播放URL失败: {title}")
                self.update_download_status(bvid, 'failed')
                return False
                
            video_url, headers = result
            
            # 设置文件路径
            filepath = os.path.join(self.save_path, filename)
            
            print(f"  开始下载: {filename}")
            
            # 下载视频
            response = self.session.get(video_url, headers=headers, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"  下载进度: {progress:.1f}%", end='\r')
            
            print(f"  下载完成: {filename}")
            self.update_download_status(bvid, 'downloaded', filename)
            return True
            
        except Exception as e:
            print(f"  下载失败 {title}: {e}")
            self.update_download_status(bvid, 'failed')
            return False

    def download_series_progressive(self, url, max_workers=3):
        """渐进式下载合集所有视频"""
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
        print(f"视频将保存到: {os.path.abspath(self.save_path)}")
        
        # 获取合集视频基本信息
        videos_basic = self.get_series_videos_basic(mid, season_id)
        
        if not videos_basic:
            print("未获取到任何视频信息")
            return
        
        total_videos = len(videos_basic)
        print(f"成功获取到 {total_videos} 个视频的基本信息")
        
        # 分析下载状态
        downloaded_count = 0
        skipped_count = 0
        for video in videos_basic:
            exists, _ = self.check_video_exists(video['title'])
            if exists:
                skipped_count += 1
        
        print(f"下载状态分析:")
        print(f"- 总视频数: {total_videos}")
        print(f"- 已下载/跳过: {skipped_count}")
        print(f"- 待下载: {total_videos - skipped_count}")
        
        # 显示视频列表
        print("\n视频列表:")
        for i, video in enumerate(videos_basic, 1):
            exists, _ = self.check_video_exists(video['title'])
            status = "✓" if exists else " "
            print(f"  {status} {i}. {video['title']}")
        
        # 询问用户是否继续下载
        if total_videos - skipped_count == 0:
            print("\n所有视频均已下载完成，无需继续下载")
            return
            
        choice = input(f"\n是否开始下载 {total_videos - skipped_count} 个未下载视频? (y/n): ")
        if choice.lower() != 'y':
            print("下载已取消")
            return
        
        # 使用线程池下载视频
        print(f"\n开始下载视频 (最大并发数: {max_workers})...")
        success_count = 0
        failed_count = 0
        
        # 过滤出未下载的视频
        videos_to_download = []
        for video in videos_basic:
            exists, _ = self.check_video_exists(video['title'])
            if not exists:
                videos_to_download.append(video)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有下载任务
            future_to_video = {
                executor.submit(self.download_single_video, video, i+1, len(videos_to_download)): video 
                for i, video in enumerate(videos_to_download)
            }
            
            # 等待任务完成
            for future in as_completed(future_to_video):
                video = future_to_video[future]
                try:
                    result = future.result()
                    if result:
                        success_count += 1
                    else:
                        failed_count += 1
                    # 添加延迟，避免请求过快
                    time.sleep(1)
                except Exception as e:
                    print(f"下载视频时发生错误: {e}")
                    failed_count += 1
        
        print(f"\n下载完成!")
        print(f"- 成功: {success_count}")
        print(f"- 失败: {failed_count}")
        print(f"- 跳过: {skipped_count}")
        print(f"- 总计: {total_videos}")
        print(f"视频保存位置: {os.path.abspath(self.save_path)}")

def main():
    # 设置下载路径
    save_path = input("请输入下载文件夹路径 (默认: ./bilibili_videos): ").strip()
    if not save_path:
        save_path = "./bilibili_videos"
    
    downloader = BilibiliSeriesDownloaderProgressive(save_path)
    
    while True:
        try:
            # 获取用户输入的网址
            url = input("\n请输入B站合集视频URL (输入'quit'退出程序): ").strip()
            
            # 检查退出条件
            if url.lower() == 'quit':
                print("程序退出")
                break
                
            # 检查网址是否为空
            if not url:
                print("网址不能为空，请重新输入")
                continue
            
            # 设置并发数
            try:
                max_workers = int(input("请输入同时下载的最大视频数 (默认: 3): ").strip() or "3")
            except:
                max_workers = 3
            
            # 开始下载
            downloader.download_series_progressive(url, max_workers)
            
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            print("请检查网址是否正确，或稍后重试")

if __name__ == "__main__":
    main()
