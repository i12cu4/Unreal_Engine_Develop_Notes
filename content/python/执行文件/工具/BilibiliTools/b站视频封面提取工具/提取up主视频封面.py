import requests
import re
import os
from urllib.parse import urlparse

def get_bilibili_cover(video_url):
    """
    获取B站视频封面图片并保存到本地
    """
    try:
        # 获取视频BV号
        if 'BV' in video_url:
            bv_pattern = r'BV[0-9A-Za-z]{10}'
            bv_id = re.search(bv_pattern, video_url).group()
        else:
            # 如果是短链接，先获取重定向后的URL
            response = requests.get(video_url, allow_redirects=True)
            final_url = response.url
            bv_pattern = r'BV[0-9A-Za-z]{10}'
            bv_id = re.search(bv_pattern, final_url).group()
        
        print(f"获取到视频BV号: {bv_id}")
        
        # 方法1: 通过B站API获取视频信息
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        
        response = requests.get(api_url, headers=headers)
        data = response.json()
        
        if data['code'] == 0:
            # 提取封面图片URL
            cover_url = data['data']['pic']
            print(f"封面图片URL: {cover_url}")
            
            # 下载图片
            img_response = requests.get(cover_url, headers=headers)
            
            # 保存图片
            filename = f"{bv_id}_cover.jpg"
            with open(filename, 'wb') as f:
                f.write(img_response.content)
            
            print(f"封面图片已保存为: {filename}")
            return filename
            
        else:
            print("获取视频信息失败")
            return None
            
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def get_bilibili_cover_alternative(video_url):
    """
    备选方法：通过解析网页获取封面
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(video_url, headers=headers)
        html_content = response.text
        
        # 在HTML中查找封面图片URL
        # B站封面通常在meta标签中
        cover_pattern = r'"og:image"\s+content="([^"]+)"'
        match = re.search(cover_pattern, html_content)
        
        if match:
            cover_url = match.group(1)
            print(f"找到封面图片URL: {cover_url}")
            
            # 下载图片
            img_response = requests.get(cover_url, headers=headers)
            
            # 从URL中提取文件名
            parsed_url = urlparse(cover_url)
            filename = os.path.basename(parsed_url.path)
            
            with open(filename, 'wb') as f:
                f.write(img_response.content)
            
            print(f"封面图片已保存为: {filename}")
            return filename
        else:
            print("未找到封面图片")
            return None
            
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def main():
    print("B站视频封面提取工具")
    print("=" * 30)
    
    while True:
        video_url = input("\n请输入B站视频网址 (输入'q'退出): ").strip()
        
        if video_url.lower() == 'q':
            break
            
        if not video_url:
            print("请输入有效的网址")
            continue
            
        print("\n尝试方法1: 通过API获取...")
        result = get_bilibili_cover(video_url)
        
        if not result:
            print("\n方法1失败，尝试方法2: 通过网页解析获取...")
            result = get_bilibili_cover_alternative(video_url)
        
        if result:
            print(f"\n✓ 成功提取封面图片: {result}")
        else:
            print("\n✗ 无法获取封面图片，请检查网址是否正确")

if __name__ == "__main__":
    main()