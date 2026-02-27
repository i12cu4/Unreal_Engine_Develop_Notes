import os
import subprocess

def convert_mov_to_mp4():
    """
    将指定文件夹中的所有MOV文件转换为MP4格式
    使用变量形式存储路径，而不是命令行参数
    """
    # 使用变量定义路径
    input_folder = r"D:\MV"  # 请替换为你的MOV文件文件夹路径
    ffmpeg_path = r"C:\Program File\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"    # 请替换为你的FFmpeg可执行文件路径
    
    # 支持的MOV文件扩展名（包括大小写变体）
    mov_extensions = ['.mov', '.MOV']
    
    # 检查输入文件夹是否存在
    if not os.path.isdir(input_folder):
        print(f"错误: 文件夹 '{input_folder}' 不存在")
        return
    
    # 检查FFmpeg是否存在
    if not os.path.isfile(ffmpeg_path):
        print(f"错误: FFmpeg路径 '{ffmpeg_path}' 不存在")
        return
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 检查文件是否为MOV格式
        if any(filename.endswith(ext) for ext in mov_extensions):
            mov_path = os.path.join(input_folder, filename)
            # 生成输出文件名（将扩展名改为.mp4）
            mp4_filename = os.path.splitext(filename)[0] + '.mp4'
            mp4_path = os.path.join(input_folder, mp4_filename)
            
            print(f"正在转换: {filename} -> {mp4_filename}")
            
            # 构建FFmpeg命令
            command = [
                ffmpeg_path,
                '-i', mov_path,      # 输入文件
                '-c:v', 'libx264',   # 视频编码器
                '-crf', '23',        # 视频质量（0-51，越低越好）
                '-preset', 'medium', # 编码速度与压缩率的平衡
                '-c:a', 'aac',       # 音频编码器
                '-b:a', '128k',      # 音频比特率
                '-y',                # 覆盖输出文件（如果存在）
                mp4_path             # 输出文件
            ]
            
            try:
                # 运行FFmpeg命令
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"完成: {mp4_filename}")
            except subprocess.CalledProcessError as e:
                print(f"转换失败: {filename}, 错误: {e}")
            except Exception as e:
                print(f"发生意外错误: {e}")

if __name__ == "__main__":
    # 调用转换函数
    convert_mov_to_mp4()