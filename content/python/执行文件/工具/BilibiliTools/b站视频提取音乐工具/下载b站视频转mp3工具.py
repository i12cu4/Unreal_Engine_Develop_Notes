import os
import re
import requests
import json
from urllib.parse import urlparse, parse_qs
import argparse
import subprocess

# 设置FFmpeg和FFprobe的绝对路径（请根据你的实际安装路径修改）
# 下载路径 https://ffmpeg.org/download.html#get-packages
FFMPEG_PATH = r"C:\Program File\ffmpeg\bin\ffmpeg.exe"  # 替换为你的ffmpeg.exe绝对路径
FFPROBE_PATH = r"C:\Program File\ffmpeg\bin\ffprobe.exe"  # 替换为你的ffprobe.exe绝对路径
SAVE_PATH = r"C:\Users\chru\Desktop\1"  # 可以修改为任意路径

class BilibiliVideoDownloader:
    def __init__(self, save_path="./downloads"):
        """
        初始化下载器
        :param save_path: 视频保存路径
        """
        self.save_path = save_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        })
        
        # 设置ffmpeg的绝对路径
        self.ffmpeg_path = FFMPEG_PATH  # Windows路径示例
        
        # 检查ffmpeg是否存在
        if not os.path.exists(self.ffmpeg_path):
            print(f"警告: 在路径 {self.ffmpeg_path} 未找到ffmpeg，MP3转换功能将不可用")
            print("请修改代码中的ffmpeg_path变量为正确的ffmpeg路径")
        
        # 创建保存目录
        if not os.path.exists(save_path):
            os.makedirs(save_path)

    def extract_bvid(self, input_str):
        """
        从输入中提取BV号，支持带有查询参数的URL
        :param input_str: 可以是BV号或B站视频URL（可以带有查询参数）
        :return: 提取到的BV号，如果提取失败返回None
        """
        # 如果是BV号格式直接返回
        if re.match(r'^BV[0-9A-Za-z]{10}$', input_str):
            return input_str
        
        # 尝试从URL中提取BV号，支持带有查询参数的URL
        bvid_patterns = [
            r'/(BV[0-9A-Za-z]{10})(?:\?|/|$)',  # 常规URL格式，可能带有查询参数
            r'bilibili\.com/video/(BV[0-9A-Za-z]{10})(?:\?|/|$)',  # 另一种URL格式
            r'^BV[0-9A-Za-z]{10}$',  # 纯BV号格式
        ]
        
        for pattern in bvid_patterns:
            match = re.search(pattern, input_str)
            if match:
                # 如果有捕获组，返回第一个捕获组；否则返回整个匹配
                return match.group(1) if match.groups() else match.group(0)
        
        return None

    def get_video_info(self, bvid):
        """
        获取视频信息
        :param bvid: 视频BV号
        :return: 视频信息字典
        """
        # 获取视频基本信息
        info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        response = self.session.get(info_url)
        data = response.json()
        
        if data['code'] != 0:
            raise Exception(f"获取视频信息失败: {data.get('message', '未知错误')}")
        
        info_data = data['data']
        cid = info_data['cid']
        title = info_data['title']
        
        # 获取视频下载链接
        play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=80&type=&otype=json"
        play_response = self.session.get(play_url)
        play_data = play_response.json()
        
        if play_data['code'] != 0:
            raise Exception(f"获取播放链接失败: {play_data.get('message', '未知错误')}")
        
        # 获取最高清晰度的视频链接
        video_url = play_data['data']['durl'][0]['url']
        
        return {
            'title': self.sanitize_filename(title),
            'video_url': video_url,
            'bvid': bvid
        }

    def sanitize_filename(self, filename):
        """
        清理文件名中的非法字符
        :param filename: 原始文件名
        :return: 清理后的文件名
        """
        # 移除或替换文件名中的非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # 限制文件名长度，避免路径过长
        if len(filename) > 100:
            filename = filename[:100]
        return filename

    def convert_mp4_to_mp3(self, mp4_path):
        """
        将MP4文件转换为MP3文件
        :param mp4_path: MP4文件路径
        :return: MP3文件路径，如果转换失败返回None
        """
        if not os.path.exists(self.ffmpeg_path):
            print("ffmpeg未找到，无法进行MP3转换")
            return None
        
        if not os.path.exists(mp4_path):
            print(f"MP4文件不存在: {mp4_path}")
            return None
        
        # 生成MP3文件路径（同目录，同名，扩展名为.mp3）
        mp3_path = os.path.splitext(mp4_path)[0] + '.mp3'
        
        try:
            print("开始转换MP4为MP3...")
            
            # 构建ffmpeg命令
            # -i 输入文件
            # -vn 不处理视频流
            # -acodec libmp3lame 使用MP3编码器
            # -q:a 0 最高音频质量（0-9，0为最高）
            # -y 覆盖输出文件
            cmd = [
                self.ffmpeg_path,
                '-i', mp4_path,
                '-vn',  # 不包含视频
                '-acodec', 'libmp3lame',  # 使用MP3编码
                '-q:a', '0',  # 最高音频质量
                '-y',  # 覆盖已存在文件
                mp3_path
            ]
            
            # 修复编码问题：使用subprocess.Popen并指定正确的编码
            # 在Windows上使用'utf-8'编码，并忽略错误
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True,  # 以文本模式处理输出
                encoding='utf-8',  # 指定编码为UTF-8
                errors='ignore'  # 忽略编码错误
            )
            
            stdout, stderr = process.communicate(timeout=300)
            
            if process.returncode == 0:
                print(f"MP3转换完成: {mp3_path}")
                return mp3_path
            else:
                print(f"MP3转换失败，错误信息: {stderr}")
                # 尝试使用不同的方法获取错误信息
                if not stderr:
                    print("ffmpeg返回非零退出码，但无法获取错误信息")
                return None
                
        except subprocess.TimeoutExpired:
            print("MP3转换超时")
            return None
        except UnicodeDecodeError as e:
            # 如果仍然有编码错误，尝试不捕获输出
            print(f"编码错误，尝试直接运行ffmpeg: {e}")
            try:
                result = subprocess.run(cmd, timeout=300, check=True)
                if result.returncode == 0:
                    print(f"MP3转换完成: {mp3_path}")
                    return mp3_path
                else:
                    print("MP3转换失败")
                    return None
            except subprocess.CalledProcessError as e:
                print(f"MP3转换失败: {e}")
                return None
            except Exception as e:
                print(f"MP3转换过程中发生错误: {e}")
                return None
        except Exception as e:
            print(f"MP3转换过程中发生错误: {e}")
            return None

    def download_video(self, video_url, filename):
        """
        下载视频文件
        :param video_url: 视频下载链接
        :param filename: 保存的文件名（不含扩展名）
        :return: 下载的文件路径
        """
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        
        # 获取视频内容
        response = self.session.get(video_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # 确定文件扩展名
        content_type = response.headers.get('content-type', '')
        if 'mp4' in content_type:
            ext = '.mp4'
        elif 'flv' in content_type:
            ext = '.flv'
        else:
            ext = '.mp4'  # 默认使用mp4
        
        filepath = os.path.join(self.save_path, f"{filename}{ext}")
        
        # 下载视频
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    # 显示下载进度
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r下载进度: {progress:.2f}% ({downloaded_size}/{total_size} bytes)", end='')
        
        print(f"\n视频下载完成: {filepath}")
        return filepath

    def download(self, input_str, convert_to_mp3=True):
        """
        主下载函数
        :param input_str: 可以是BV号或B站视频URL（可以带有查询参数）
        :param convert_to_mp3: 是否转换为MP3
        :return: 下载的文件路径和转换后的MP3路径（如果有）
        """
        # 提取BV号
        bvid = self.extract_bvid(input_str)
        if not bvid:
            raise ValueError("无法从输入中提取BV号")
        
        print(f"提取到BV号: {bvid}")
        
        # 获取视频信息  
        print("获取视频信息中...")
        video_info = self.get_video_info(bvid)
        
        print(f"视频标题: {video_info['title']}")
        print("开始下载视频...")
        
        # 下载视频
        filepath = self.download_video(video_info['video_url'], video_info['title'])
        
        mp3_path = None
        # 如果下载的是MP4文件且需要转换为MP3
        if convert_to_mp3 and filepath.lower().endswith('.mp4'):
            print("开始转换为MP3格式...")
            mp3_path = self.convert_mp4_to_mp3(filepath)
        
        return filepath, mp3_path

def main():
    parser = argparse.ArgumentParser(description='B站视频下载工具')
    parser.add_argument('input', help='B站视频BV号或URL（可以带有查询参数）')
    parser.add_argument('-o', '--output', default='./downloads', help='视频保存路径，默认为./downloads')
    parser.add_argument('--no-convert', action='store_true', help='不自动转换为MP3')
    
    args = parser.parse_args()
    
    try:
        downloader = BilibiliVideoDownloader(args.output)
        downloader.download(args.input, convert_to_mp3=not args.no_convert)
    except Exception as e:
        print(f"下载失败: {e}")

if __name__ == "__main__":    
    # 创建下载器实例
    downloader = BilibiliVideoDownloader(SAVE_PATH)
    
    # 持续输入网址进行下载
    while True:
        try:
            # 获取用户输入的网址
            url = input("请输入B站视频网址（输入'quit'退出程序）: ").strip()
            
            # 检查退出条件
            if url.lower() == 'quit':
                print("程序退出")
                break
                
            # 检查网址是否为空
            if not url:
                print("网址不能为空，请重新输入")
                continue
            
            # 下载视频
            print(f"开始下载: {url}")
            video_path, mp3_path = downloader.download(url, True)
            
            if mp3_path:
                print(f"MP3文件已生成: {mp3_path}")
            print("下载完成！")
            
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            print(f"下载失败: {e}")
            print("请检查网址是否正确，或稍后重试")