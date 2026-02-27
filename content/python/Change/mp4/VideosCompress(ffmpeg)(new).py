import subprocess
import os
import logging
import math
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_frame_rate(frame_rate_str: str) -> float:
    """解析帧率字符串，返回浮点数形式的帧率"""
    if '/' in frame_rate_str:
        try:
            numerator, denominator = frame_rate_str.split('/')
            return float(numerator) / float(denominator)
        except (ValueError, ZeroDivisionError):
            logger.warning(f"无法解析帧率: {frame_rate_str}")
            return 30.0  # 默认值
    else:
        try:
            return float(frame_rate_str)
        except ValueError:
            logger.warning(f"无法解析帧率: {frame_rate_str}")
            return 30.0  # 默认值

def get_video_info(video_path: str, ffprobe_path: str) -> Dict[str, str]:
    """获取视频信息"""
    try:
        cmd = [
            ffprobe_path,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,avg_frame_rate,duration,bit_rate",
            "-of", "default=noprint_wrappers=1",
            video_path,
        ]
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        info = dict(line.split("=") for line in result.stdout.splitlines())
        
        # 计算帧率（处理分数形式的帧率）
        if 'avg_frame_rate' in info:
            info['frame_rate_float'] = str(parse_frame_rate(info['avg_frame_rate']))
        
        return info
    except subprocess.CalledProcessError as e:
        logger.error(f"获取视频信息失败: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"处理视频信息时发生错误: {str(e)}")
        raise

def calculate_scaled_dimensions(
    original_width: int, 
    original_height: int, 
    target_width: int, 
    target_height: int,
    keep_aspect_ratio: bool = True
) -> Tuple[int, int]:
    """
    计算缩放后的尺寸，考虑保持宽高比
    
    返回:
        Tuple[int, int]: (width, height)
    """
    # 如果原始分辨率已经小于目标分辨率，使用原始分辨率
    if original_width <= target_width and original_height <= target_height:
        return original_width, original_height
    
    # 如果不保持宽高比，直接使用目标分辨率
    if not keep_aspect_ratio:
        return min(original_width, target_width), min(original_height, target_height)
    
    # 保持宽高比的情况下计算缩放尺寸
    original_ratio = original_width / original_height
    target_ratio = target_width / target_height
    
    if original_ratio >= target_ratio:
        # 以宽度为基准缩放
        scaled_width = min(original_width, target_width)
        scaled_height = int(scaled_width / original_ratio)
    else:
        # 以高度为基准缩放
        scaled_height = min(original_height, target_height)
        scaled_width = int(scaled_height * original_ratio)
    
    # 确保尺寸是偶数（某些编码器要求）
    scaled_width = scaled_width - (scaled_width % 2)
    scaled_height = scaled_height - (scaled_height % 2)
    
    return scaled_width, scaled_height

def calculate_optimal_crf(input_path, ffprobe_path, min_crf=23, max_crf=28):
    """根据原始视频的比特率计算最优CRF值"""
    try:
        # 获取原始视频信息
        video_info = get_video_info(input_path, ffprobe_path)
        
        # 获取原始视频的比特率（如果可用）
        original_bitrate = video_info.get('bit_rate', None)
        if original_bitrate and original_bitrate != 'N/A':
            original_bitrate = int(original_bitrate) / 1000  # 转换为kbps
            
            # 根据原始比特率动态调整CRF
            if original_bitrate < 1000:  # 低比特率视频
                return min(max_crf, 26)  # 使用较高的CRF
            elif original_bitrate > 5000:  # 高比特率视频
                return max(min_crf, 20)  # 使用较低的CRF
            else:  # 中等比特率视频
                return (min_crf + max_crf) // 2
        else:
            # 无法获取比特率时使用默认值
            return 23
    except:
        return 23  # 出错时使用默认值

def optimize_video(
    input_path: str,
    output_path: str,
    target_width: int,
    target_height: int,
    target_frame_rate: int,
    ffmpeg_path: str,
    crf: int = 23,
    bit: str = "64k",
    ac: int = 1,
    keep_aspect_ratio: bool = True
) -> bool:
    """优化视频"""
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 如果输出文件已存在，询问是否覆盖
        if os.path.exists(output_path):
            response = input(f"文件 {output_path} 已存在，是否覆盖？(y/n): ")
            if response.lower() != 'y':
                logger.info(f"跳过已存在的文件: {output_path}")
                return False
        
        # 获取视频信息以确定实际使用的参数
        ffprobe_path = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
        video_info = get_video_info(input_path, ffprobe_path)
        
        original_width = int(video_info['width'])
        original_height = int(video_info['height'])
        original_frame_rate = float(video_info.get('frame_rate_float', 30.0))
        
        # 确定实际使用的帧率（取原始帧率和目标帧率中较小的）
        actual_frame_rate = min(original_frame_rate, target_frame_rate)
        
        # 计算实际使用的分辨率
        actual_width, actual_height = calculate_scaled_dimensions(
            original_width, original_height, target_width, target_height, keep_aspect_ratio
        )
        
        logger.info(f"原始: {original_width}x{original_height} @ {original_frame_rate:.2f}fps")
        logger.info(f"目标: {target_width}x{target_height} @ {target_frame_rate}fps")
        logger.info(f"实际: {actual_width}x{actual_height} @ {actual_frame_rate:.2f}fps")
        logger.info(f"使用CRF: {crf}")
        
        # 构建ffmpeg命令
        cmd = [
            ffmpeg_path,
            "-i", input_path,
            "-vf", f"scale={actual_width}:{actual_height}",
            "-r", str(actual_frame_rate),
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", bit,
            "-ac", str(ac),
            "-y",  # 自动覆盖输出文件
            output_path,
        ]
        
        # 执行命令并显示进度
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 实时输出处理信息
        for line in process.stdout:
            if "time=" in line:
                logger.info(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            # 获取输出文件大小
            output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            input_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
            compression_ratio = (1 - output_size / input_size) * 100
            
            logger.info(
                f"处理完成: {actual_width}x{actual_height} @ {actual_frame_rate:.2f}fps | "
                f"压缩率: {compression_ratio:.1f}% ({input_size:.1f}MB -> {output_size:.1f}MB)"
            )
            return True
        else:
            logger.error(f"处理失败: {output_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg处理失败: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"处理视频时发生错误: {str(e)}")
        return False

def optimize_video_with_size_check(
    input_path: str,
    output_path: str,
    target_width: int,
    target_height: int,
    target_frame_rate: int,
    ffmpeg_path: str,
    initial_crf: int = 23,
    bit: str = "64k",
    ac: int = 1,
    keep_aspect_ratio: bool = True,
    max_retries: int = 3
) -> bool:
    """优化视频，并确保输出文件不大于输入文件"""
    original_size = os.path.getsize(input_path)
    best_crf = initial_crf
    best_output_path = None
    
    # 获取ffprobe路径
    ffprobe_path = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
    
    # 计算初始CRF值
    initial_crf = calculate_optimal_crf(input_path, ffprobe_path, min_crf=23, max_crf=28)
    logger.info(f"计算得到初始CRF值: {initial_crf}")
    
    for attempt in range(max_retries):
        current_crf = initial_crf + attempt * 2  # 每次尝试增加CRF值
        temp_output_path = output_path.replace(".mp4", f"_temp_{current_crf}.mp4")
        
        # 优化视频
        success = optimize_video(
            input_path,
            temp_output_path,
            target_width,
            target_height,
            target_frame_rate,
            ffmpeg_path,
            current_crf,
            bit,
            ac,
            keep_aspect_ratio
        )
        
        if success:
            # 检查文件大小
            compressed_size = os.path.getsize(temp_output_path)
            
            if compressed_size < original_size:
                # 找到可接受的压缩结果
                best_crf = current_crf
                best_output_path = temp_output_path
                logger.info(f"找到可接受的CRF值: {current_crf}")
                break
            else:
                # 删除过大的文件
                os.remove(temp_output_path)
                logger.info(f"尝试 CRF={current_crf} 结果过大，继续尝试更高CRF")
        else:
            logger.error(f"尝试 CRF={current_crf} 时压缩失败")
    
    # 处理最佳结果
    if best_output_path:
        # 重命名最佳结果文件
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(best_output_path, output_path)
        
        compressed_size = os.path.getsize(output_path)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        logger.info(
            f"最终使用 CRF={best_crf} | "
            f"压缩率: {compression_ratio:.1f}% | "
            f"大小: {original_size/1024/1024:.1f}MB -> {compressed_size/1024/1024:.1f}MB"
        )
        return True
    else:
        logger.error(f"所有尝试均未获得更小的文件大小")
        return False

def list_mp4_files(filepath: str) -> List[str]:
    """列出目录中的所有MP4文件（不含扩展名）"""
    mp4_files = []
    path = Path(filepath)
    
    for file in path.glob("*.mp4"):
        mp4_files.append(file.stem)
    
    return mp4_files

def main():
    # 配置路径和参数
    ffmpeg_path = r"C:\Program File\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
    
    # 验证FFmpeg是否存在
    if not os.path.isfile(ffmpeg_path):
        logger.error(f"FFmpeg未找到于: {ffmpeg_path}")
        return
    
    # 设置视频参数
    pixel_xs = [1280]  # 宽度列表
    pixel_ys = [720]   # 高度列表 
    frame_rates = [30] # 帧率列表
    initial_crf = 23   # 初始CRF值
    bit_rates = ["64k"] # 音频比特率列表
    audio_channels = [1] # 音频通道数列表
    keep_aspect_ratio = True  # 是否保持宽高比
    file_path = r"D:\MV\2\\"  # 视频文件路径
    
    # 获取所有MP4文件
    origin_filenames = list_mp4_files(file_path)
    logger.info(f"找到 {len(origin_filenames)} 个MP4文件: {origin_filenames}")
    
    if not origin_filenames:
        logger.warning("未找到MP4文件，程序退出")
        return
    
    # 处理每个视频文件
    for origin_filename in origin_filenames:
        input_video_path = os.path.join(file_path, origin_filename + ".mp4")
        
        # 检查输入文件是否存在
        if not os.path.isfile(input_video_path):
            logger.error(f"输入文件不存在: {input_video_path}")
            continue
        
        try:
            # 获取视频信息
            ffprobe_path = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
            video_info = get_video_info(input_video_path, ffprobe_path)
            
            original_width = int(video_info['width'])
            original_height = int(video_info['height'])
            original_frame_rate = float(video_info.get('frame_rate_float', 30.0))
            original_size = os.path.getsize(input_video_path) / (1024 * 1024)  # MB
            
            logger.info(
                f"原始视频: {origin_filename} | "
                f"分辨率: {original_width}x{original_height} | "
                f"帧率: {original_frame_rate:.2f}fps | "
                f"大小: {original_size:.1f}MB"
            )
            
            origin_name = origin_filename.split("_")[0]
            
            # 生成所有参数组合并处理
            for pixel_x in pixel_xs:
                for pixel_y in pixel_ys:
                    for target_frame_rate in frame_rates:
                        for bit in bit_rates:
                            for ac in audio_channels:
                                # 构建输出路径
                                output_filename = (
                                    f"{origin_name}_{pixel_x}x{pixel_y}_"
                                    f"f{target_frame_rate}_H.libx264_"
                                    f"b{bit}_ac{ac}.mp4"
                                )
                                output_video_path = os.path.join(file_path, output_filename)
                                
                                # 显示处理信息
                                logger.info(f"开始处理: {output_filename}")
                                
                                # 优化视频（带大小检查）
                                success = optimize_video_with_size_check(
                                    input_video_path,
                                    output_video_path,
                                    pixel_x,
                                    pixel_y,
                                    target_frame_rate,
                                    ffmpeg_path,
                                    initial_crf,
                                    bit,
                                    ac,
                                    keep_aspect_ratio
                                )
                                
                                if success:
                                    logger.info(f"完成: {output_filename}")
                                else:
                                    logger.error(f"失败: {output_filename}")
                                    
        except Exception as e:
            logger.error(f"处理视频 {origin_filename} 时发生错误: {str(e)}")
            continue

    logger.info("所有处理完成")

if __name__ == "__main__":
    main()