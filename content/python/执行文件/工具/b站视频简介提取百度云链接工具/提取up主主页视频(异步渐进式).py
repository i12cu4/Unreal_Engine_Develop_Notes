import os
import re
import requests
import json
import time
import random
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

class BilibiliUpDownloader:
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
        self.status_file = os.path.join(save_path, "up_download_status.json")
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

    def extract_mid(self, url):
        """从UP主主页URL中提取mid"""
        try:
            parsed_url = urlparse(url)
            # 从路径中提取数字mid
            path_parts = [p for p in parsed_url.path.split('/') if p]
            for part in path_parts:
                if part.isdigit():
                    return part
            
            # 从查询参数中查找
            query_params = parse_qs(parsed_url.query)
            if 'mid' in query_params:
                return query_params['mid'][0]
                
        except Exception as e:
            print(f"提取mid失败: {e}")
        
        return None

    def get_up_videos(self, mid, page_size=30, max_pages=50):
        """获取UP主所有视频（分页获取）"""
        all_videos = []
        page_num = 1
        total_videos = 0
        
        print("正在获取UP主视频列表...")
        
        while page_num <= max_pages:
            try:
                # 使用随机延迟避免请求过快
                delay = random.uniform(2, 5)  # 2-5秒随机延迟
                time.sleep(delay)
                
                # 使用B站API获取UP主视频列表
                api_url = f"https://api.bilibili.com/x/space/arc/search"
                params = {
                    'mid': mid,
                    'ps': page_size,
                    'pn': page_num,
                    'order': 'pubdate'  # 按发布时间排序
                }
                
                print(f"正在请求第 {page_num} 页...")
                response = self.session.get(api_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data['code'] != 0:
                    error_msg = data.get('message', '未知错误')
                    print(f"获取第 {page_num} 页视频列表失败: {error_msg}")
                    
                    # 如果是频率限制，等待更长时间后重试
                    if "频繁" in error_msg or data['code'] == -412:
                        print("遇到频率限制，等待10秒后重试...")
                        time.sleep(10)
                        continue  # 不增加页码，重试当前页
                    else:
                        break  # 其他错误直接退出
                
                vlist = data['data']['list']['vlist']
                if not vlist:
                    print("没有更多视频了")
                    break
                
                # 获取当前页的视频总数和总视频数
                current_count = len(vlist)
                if page_num == 1:
                    total_videos = data['data']['page']['count']
                    print(f"UP主共有 {total_videos} 个视频")
                    print(f"预计需要获取 {min((total_videos + page_size - 1) // page_size, max_pages)} 页")
                
                print(f"成功获取第 {page_num} 页，共 {current_count} 个视频")
                
                # 处理当前页的视频
                for item in vlist:
                    video_info = {
                        'title': item.get('title', ''),
                        'bvid': item.get('bvid', ''),
                        'aid': item.get('aid', ''),
                        'created': item.get('created', 0),
                        'length': item.get('length', ''),
                        'play': item.get('play', 0),
                        'comment': item.get('comment', 0)
                    }
                    all_videos.append(video_info)
                
                # 检查是否已获取所有视频
                if len(all_videos) >= total_videos:
                    print(f"已获取所有 {len(all_videos)} 个视频")
                    break
                    
                # 检查是否已经到达最后一页
                page_info = data['data']['page']
                if page_info['pn'] * page_info['ps'] >= page_info['count']:
                    print(f"已获取所有 {len(all_videos)} 个视频（通过页面信息判断）")
                    break
                    
                page_num += 1
                
            except requests.exceptions.RequestException as e:
                print(f"网络请求异常 (第 {page_num} 页): {e}")
                # 等待后重试当前页
                time.sleep(5)
            except Exception as e:
                print(f"获取第 {page_num} 页视频失败: {e}")
                # 等待后继续下一页
                time.sleep(3)
                page_num += 1
        
        return all_videos

    def get_video_detail(self, bvid):
        """获取单个视频的详细信息，包括cid"""
        try:
            # 添加随机延迟
            time.sleep(random.uniform(1, 2))
            
            # 使用B站API获取视频详细信息
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 0:
                video_data = data['data']
                return {
                    'title': self.sanitize_filename(video_data.get('title', '')),
                    'bvid': video_data.get('bvid', ''),
                    'cid': video_data.get('cid', ''),
                    'desc': video_data.get('desc', ''),
                    'duration': video_data.get('duration', 0),
                    'pubdate': video_data.get('pubdate', 0)
                }
            else:
                print(f"获取视频{bvid}详情失败: {data['message']}")
                return None
                
        except Exception as e:
            print(f"请求视频详情失败: {e}")
            return None

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
            # 添加随机延迟
            time.sleep(random.uniform(1, 2))
            
            # 获取视频下载链接
            play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=80&type=&otype=json"
            response = self.session.get(play_url, timeout=10)
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
            
            print(f"[{index}/{total}] 开始处理: {title}")
            
            # 检查视频是否已存在
            exists, filename = self.check_video_exists(title)
            if exists:
                print(f"  视频已存在，跳过: {filename}")
                self.update_download_status(bvid, 'skipped', filename)
                return True
            
            # 获取视频详细信息（包含cid）
            video_detail = self.get_video_detail(bvid)
            if not video_detail:
                print(f"  获取视频详情失败: {title}")
                self.update_download_status(bvid, 'failed')
                return False
            
            cid = video_detail['cid']
            
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
            response = self.session.get(video_url, headers=headers, stream=True, timeout=30)
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

    def download_up_videos(self, url, max_workers=3):
        """下载UP主所有视频"""
        print("开始获取B站UP主信息...")
        
        # 提取mid
        mid = self.extract_mid(url)
        if not mid:
            print("无法从URL中提取UP主ID")
            return
        
        print(f"获取到UP主ID: {mid}")
        print(f"视频将保存到: {os.path.abspath(self.save_path)}")
        
        # 获取UP主所有视频
        videos_basic = self.get_up_videos(mid)
        
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
        
        # 显示视频列表（前10个）
        print("\n前10个视频列表:")
        for i, video in enumerate(videos_basic[:10], 1):
            exists, _ = self.check_video_exists(video['title'])
            status = "✓" if exists else " "
            play_count = f"播放:{video.get('play', 0)}"
            print(f"  {status} {i}. {video['title']} ({play_count})")
        
        if total_videos > 10:
            print(f"  ... 还有 {total_videos - 10} 个视频")
        
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
                    time.sleep(random.uniform(2, 4))
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
    
    downloader = BilibiliUpDownloader(save_path)
    
    while True:
        try:
            # 获取用户输入的网址
            url = input("\n请输入B站UP主主页URL (输入'quit'退出程序): ").strip()
            
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
            downloader.download_up_videos(url, max_workers)
            
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            print("请检查网址是否正确，或稍后重试")

if __name__ == "__main__":
    main()
