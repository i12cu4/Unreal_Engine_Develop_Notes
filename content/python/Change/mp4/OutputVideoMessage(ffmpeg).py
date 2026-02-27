# 输出视频相关参数(需要配置ffmpeg)
import subprocess
import os


def get_video_info(video_path, ffprobe_path):
    # 构建ffprobe命令，用于获取视频信息
    cmd = [
        ffprobe_path,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,avg_frame_rate",
        "-of",
        "default=noprint_wrappers=1",
        video_path,
    ]
    # 执行命令并获取输出结果
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
    )
    # 将输出结果转换为字典格式
    return dict(line.split("=") for line in result.stdout.splitlines())


# ffmpeg和ffprobe的路径
ffmpeg_path = r"C:\Program File\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
ffprobe_path = r"C:\Program File\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe"

# 设置视频参数
input_video_path = r"D:\task\Moive.mp4"

# 获取视频信息并打印
print(get_video_info(input_video_path, ffprobe_path))
# video_info = get_video_info(input_video_path+".mp4", ffprobe_path)
# print(f"Original resolution: {video_info['width']}x{video_info['height']}, Frame rate: {video_info['avg_frame_rate']}")
