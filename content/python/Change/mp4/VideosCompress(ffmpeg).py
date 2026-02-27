# 视频批量压缩
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


def optimize_video(
    input_path,
    output_path,
    target_width,
    target_height,
    target_frame_rate,
    ffmpeg_path,
    crf=23,
    bit="64k",
    ac=1,
):
    # 构建ffmpeg命令，用于视频优化
    cmd = [
        ffmpeg_path,
        "-i",
        input_path,
        "-vf",
        f"scale={target_width}:{target_height}",  # 视频缩放
        "-r",
        str(target_frame_rate),  # 设置帧率
        "-c:v",
        "libx264",  # 设置视频编码格式
        "-crf",
        str(crf),  # 设置视频质量
        "-preset",
        "fast",  # 设置编码速度
        "-c:a",
        "aac",  # 设置音频编码格式
        "-b:a",
        bit,  # 设置音频比特率
        "-ac",
        str(ac),  # 设置音频通道数
        output_path,  # 输出文件路径
    ]
    # 执行命令
    subprocess.run(cmd, check=True)
    # 打印完成信息
    print(f"file {target_width}x{target_height} FPS{target_frame_rate} Done")


# ffmpeg和ffprobe的路径
ffmpeg_path = r"C:\Program File\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
ffprobe_path = r"C:\Program File\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe"

# 设置视频参数
pixel_xs = [720]  # [2712,1920,1280,720]
pixel_ys = [480]  # [1220,1080,720,576,480]
frame_rates = [30]  # 帧率列表
crfs = [18]  # [18,20,22,24,26,28,30,32]#[18, 24, 28]  # CRF值列表
bit_rates = ["64k"]  # 音频比特率列表
audio_channels = [1]  # 音频通道数列表
file_path = r"C:\Users\admin\Downloads\m\\"  # 该路径下有两个视频文件

origin_filenames = ["7M_1280x576_f30_H.libx264_douyin_b128k_ac2"]  # ,
# "7M2_1280x576_f30_H.libx264_douyin_b128k_ac22"] # 注意:要省去 '.mp4' 后缀

"""
#当然,你怕麻烦你可以用指定路径下所有的mp4视频进行压缩,不用自己手动输入文件名
def list_mp4_files_without_extension(filepath):
    # 初始化一个空列表，用于存储.mp4文件的文件名（不包含扩展名）
    origin_filenames_without_extension = []

    # 遍历给定路径下的所有文件和文件夹
    for root, dirs, files in os.walk(filepath):
        for file in files:
            # 检查文件是否以.mp4结尾
            if file.lower().endswith(".mp4"):
                # 移除文件名的.mp4后缀
                filename_without_extension = os.path.splitext(file)[0]
                # 将处理后的文件名添加到列表中
                origin_filenames_without_extension.append(filename_without_extension)

    return origin_filenames_without_extension
    
origin_filenames = list_mp4_files_without_extension(file_path)

print(origin_filenames) 
# -> ['7M2_1280x576_f30_H.libx264_douyin_b128k_ac22', '7M_1280x576_f30_H.libx264_douyin_b128k_ac2']
"""

# 遍历所有视频开始压缩
for origin_filename in origin_filenames:
    input_video_path = file_path + origin_filename
    # 获取视频信息并打印
    video_info = get_video_info(input_video_path + ".mp4", ffprobe_path)
    print(
        f"Original resolution: {video_info['width']}x{video_info['height']}, "
        f"Frame rate: {video_info['avg_frame_rate']}"
    )

    origin_name = origin_filename.split("_")[0]
    print(origin_name)
    # 遍历所有参数组合以生成多个视频
    for pixel_x in pixel_xs:
        if pixel_x > int(video_info["width"]):
            continue
        for pixel_y in pixel_ys:
            if pixel_y > int(video_info["height"]):
                continue
            for target_frame_rate in frame_rates:
                if target_frame_rate > int(video_info["avg_frame_rate"].split("/")[0]):
                    continue
                for crf in crfs:
                    for bit in bit_rates:
                        for ac in audio_channels:
                            # 构建输出视频路径
                            origin_path = file_path + origin_name
                            output_video_path = (
                                f"{origin_path}_{pixel_x}x{pixel_y}_"
                                f"f{target_frame_rate}_H.libx264_"
                                f"crf{crf}_b{bit}_ac{ac}.mp4"
                            )
                            # 优化视频
                            optimize_video(
                                input_video_path + ".mp4",
                                output_video_path,
                                pixel_x,
                                pixel_y,
                                target_frame_rate,
                                ffmpeg_path,
                                crf,
                                bit,
                                ac,
                            )

print("Done")
