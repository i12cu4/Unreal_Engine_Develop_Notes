import os
import subprocess
import sys
import json

# 设置FFmpeg和FFprobe的绝对路径（请根据你的实际安装路径修改）
# 下载路径 https://ffmpeg.org/download.html#get-packages
FFMPEG_PATH = r"C:\Program File\ffmpeg\bin\ffmpeg.exe"  # 替换为你的ffmpeg.exe绝对路径
FFPROBE_PATH = r"C:\Program File\ffmpeg\bin\ffprobe.exe"  # 替换为你的ffprobe.exe绝对路径

# 直接设置目录路径变量
directory_path = r"C:\Users\chru\Desktop\1"

def extract_audio_from_mp4(input_path, output_path=None):
    """
    从MP4文件中提取音频并保存为MP3文件
    
    Args:
        input_path (str): 输入的MP4文件路径
        output_path (str, optional): 输出的MP3文件路径。如果未提供，则使用与输入文件相同的路径和名称，但扩展名为.mp3
    """
    # 检查输入文件是否存在
    if not os.path.isfile(input_path):
        print(f"错误：文件 '{input_path}' 不存在")
        return False
    
    # 如果未提供输出路径，则生成一个
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".mp3"
    
    # 检查输出文件是否已存在
    if os.path.exists(output_path):
        print(f"跳过: MP3文件已存在 '{output_path}'")
        return True
    
    # 获取原始视频的音频信息
    sample_rate = None
    channels = None
    bitrate = None
    
    try:
        # 使用ffprobe获取音频信息（JSON格式）
        cmd_probe = [
            FFPROBE_PATH,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-select_streams', 'a',
            input_path
        ]
        
        # 设置编码为UTF-8以避免解码错误
        result = subprocess.run(cmd_probe, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            
            if 'streams' in data and len(data['streams']) > 0:
                stream = data['streams'][0]
                sample_rate = stream.get('sample_rate')
                channels = stream.get('channels')
                
                # 获取比特率
                bitrate = stream.get('bit_rate')
                if not bitrate:
                    # 如果没有流级别的比特率，尝试获取格式级别的比特率
                    cmd_format = [
                        FFPROBE_PATH,
                        '-v', 'quiet',
                        '-print_format', 'json',
                        '-show_format',
                        input_path
                    ]
                    
                    format_result = subprocess.run(cmd_format, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                    if format_result.returncode == 0 and format_result.stdout:
                        format_data = json.loads(format_result.stdout)
                        bitrate = format_data.get('format', {}).get('bit_rate')
        
        print(f"检测到原始音频参数: 采样率={sample_rate}Hz, 通道数={channels}, 码率={bitrate}bps")
        
    except Exception as e:
        print(f"获取音频信息时出错: {e}")
    
    # 构建ffmpeg命令
    cmd = [FFMPEG_PATH, '-i', input_path, '-vn', '-acodec', 'libmp3lame']
    
    # 添加音频参数（如果可用）
    if sample_rate and sample_rate.isdigit() and int(sample_rate) > 0:
        cmd.extend(['-ar', sample_rate])
    if channels and str(channels).isdigit() and int(channels) > 0:
        cmd.extend(['-ac', str(channels)])
    if bitrate and bitrate.isdigit() and int(bitrate) > 0:
        cmd.extend(['-b:a', bitrate])
    else:
        cmd.extend(['-q:a', '0'])  # 最高质量
    
    cmd.append('-y')
    cmd.append(output_path)
    
    # 执行转换
    try:
        print(f"正在提取音频到: {output_path}")
        
        # 设置编码为UTF-8以避免解码错误
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print("转换完成!")
            return True
        else:
            print(f"转换失败，返回码: {result.returncode}")
            if result.stderr:
                print(f"错误输出: {result.stderr}")
            return False
    except Exception as e:
        print(f"发生未知错误: {e}")
        return False

def process_directory(directory_path):
    """
    处理指定目录中的所有MP4文件
    
    Args:
        directory_path (str): 要处理的目录路径
    """
    # 检查目录是否存在
    if not os.path.isdir(directory_path):
        print(f"错误: 目录 '{directory_path}' 不存在")
        return
    
    # 查找所有MP4文件
    try:
        files = os.listdir(directory_path)
        mp4_files = [f for f in files if f.lower().endswith('.mp4')]
    except Exception as e:
        print(f"无法读取目录中的文件列表: {e}")
        return
    
    if not mp4_files:
        print(f"在目录 '{directory_path}' 中未找到MP4文件")
        return
    
    print(f"找到 {len(mp4_files)} 个MP4文件")
    
    # 处理每个MP4文件
    for mp4_file in mp4_files:
        try:
            input_path = os.path.join(directory_path, mp4_file)
            print(f"\n处理文件: {mp4_file}")
            extract_audio_from_mp4(input_path)
        except Exception as e:
            print(f"处理文件 {mp4_file} 时出错: {e}")

if __name__ == "__main__":
    
    # 检查FFmpeg路径是否正确
    if not os.path.isfile(FFMPEG_PATH):
        print(f"错误: 在指定路径未找到ffmpeg: {FFMPEG_PATH}")
        print("请修改代码中的FFMPEG_PATH变量为你的ffmpeg.exe实际路径")
        sys.exit(1)
    
    if not os.path.isfile(FFPROBE_PATH):
        print(f"错误: 在指定路径未找到ffprobe: {FFPROBE_PATH}")
        print("请修改代码中的FFPROBE_PATH变量为你的ffprobe.exe实际路径")
        sys.exit(1)
    
    # 处理目录中的所有MP4文件
    process_directory(directory_path)
