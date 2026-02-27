from pytube import YouTube
import os

def download_youtube_video(video_url, download_path):
    try:
        # 创建YouTube对象，添加use_oauth和allow_oauth_cache参数
        yt = YouTube(video_url, use_oauth=False, allow_oauth_cache=False)
        
        print(f"正在下载: {yt.title}")
        print(f"频道: {yt.author}")
        print(f"视频时长: {yt.length} 秒")
        
        # 获取最高质量的渐进式视频流
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            stream = yt.streams.get_highest_resolution()
        
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            print(f"创建目录: {download_path}")
        
        print(f"开始下载到: {download_path}")
        output_file = stream.download(output_path=download_path)
        filename = os.path.basename(output_file)
        print(f"下载完成: {filename}")
        return output_file
        
    except Exception as e:
        print(f"下载过程中出现错误: {str(e)}")
        return None

if __name__ == "__main__":
    DOWNLOAD_DIR = r"C:\Users\chru\Downloads"  # 请修改为你的路径
    VIDEO_URL = input("请输入YouTube视频网址: ").strip()
    if VIDEO_URL:
        download_youtube_video(VIDEO_URL, DOWNLOAD_DIR)
    else:
        print("未输入视频网址！")


