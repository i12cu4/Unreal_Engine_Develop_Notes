import os
import sys
import subprocess
import json
import shutil

# ------------------------------------------------------------
# 自动查找 FFmpeg 和 FFprobe
# ------------------------------------------------------------
def find_ffmpeg():
    """从 PATH 或常见安装路径查找 ffmpeg.exe 和 ffprobe.exe"""
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        return ffmpeg, ffprobe

    # 常见安装目录（按优先级）
    common_paths = [
        r"C:\Program Files\ffmpeg\bin",
        r"C:\Program Files (x86)\ffmpeg\bin",
        r"C:\ffmpeg\bin",
        os.path.join(os.environ.get("USERPROFILE", ""), "ffmpeg", "bin"),
    ]
    for base in common_paths:
        exe = os.path.join(base, "ffmpeg.exe")
        probe = os.path.join(base, "ffprobe.exe")
        if os.path.isfile(exe) and os.path.isfile(probe):
            return exe, probe
    return None, None

FFMPEG_PATH, FFPROBE_PATH = find_ffmpeg()
if not FFMPEG_PATH:
    print("❌ 未找到 ffmpeg/ffprobe，请安装 FFmpeg 并将其 bin 目录添加到系统 PATH 中。")
    print("   下载地址: https://ffmpeg.org/download.html")
    input("按 Enter 键退出...")
    sys.exit(1)

# ------------------------------------------------------------
# 核心转换函数
# ------------------------------------------------------------
def extract_audio_from_mp4(input_path, output_path=None, overwrite=False):
    """
    将 MP4 文件提取音频为 MP3
    返回 True 表示成功或跳过，False 表示失败
    """
    if not os.path.isfile(input_path):
        print(f"⚠️  文件不存在: {input_path}")
        return False

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".mp3"

    if not overwrite and os.path.exists(output_path):
        print(f"⏭️  跳过 (MP3 已存在): {output_path}")
        return True

    # 获取原始音频参数
    sample_rate = None
    channels = None
    bitrate = None

    try:
        # 使用 ffprobe 获取音频流信息
        cmd_probe = [
            FFPROBE_PATH,
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-select_streams", "a",
            input_path
        ]
        result = subprocess.run(cmd_probe, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            if "streams" in data and data["streams"]:
                stream = data["streams"][0]
                sample_rate = stream.get("sample_rate")
                channels = stream.get("channels")
                bitrate = stream.get("bit_rate")
                if not bitrate:
                    # 尝试从 format 中获取
                    cmd_format = [
                        FFPROBE_PATH,
                        "-v", "quiet",
                        "-print_format", "json",
                        "-show_format",
                        input_path
                    ]
                    fmt_res = subprocess.run(cmd_format, capture_output=True, text=True, encoding="utf-8", errors="ignore")
                    if fmt_res.returncode == 0 and fmt_res.stdout:
                        fmt_data = json.loads(fmt_res.stdout)
                        bitrate = fmt_data.get("format", {}).get("bit_rate")
        print(f"🎵 检测到音频参数: 采样率={sample_rate}Hz, 声道={channels}, 码率={bitrate}bps")
    except Exception as e:
        print(f"⚠️  获取音频信息失败: {e}，将使用默认高质量参数")

    # 构建 ffmpeg 命令
    cmd = [FFMPEG_PATH, "-i", input_path, "-vn", "-acodec", "libmp3lame"]

    if sample_rate and sample_rate.isdigit() and int(sample_rate) > 0:
        cmd.extend(["-ar", sample_rate])
    if channels and str(channels).isdigit() and int(channels) > 0:
        cmd.extend(["-ac", str(channels)])
    if bitrate and bitrate.isdigit() and int(bitrate) > 0:
        cmd.extend(["-b:a", bitrate])
    else:
        cmd.extend(["-q:a", "0"])   # 最高质量（VBR）

    cmd.append("-y")  # 覆盖输出（但我们已经检查过存在性，还是加上确保）
    cmd.append(output_path)

    try:
        print(f"🔄 正在转换: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if result.returncode == 0:
            print("✅ 转换成功")
            return True
        else:
            print(f"❌ 转换失败 (返回码 {result.returncode})")
            if result.stderr:
                print(f"   错误信息: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ 发生异常: {e}")
        return False

# ------------------------------------------------------------
# 递归处理文件/文件夹
# ------------------------------------------------------------
def process_path(path, overwrite=False):
    """处理一个路径（文件或文件夹），如果是文件夹则递归查找 MP4"""
    if not os.path.exists(path):
        print(f"⚠️  路径不存在: {path}")
        return

    if os.path.isfile(path):
        # 只处理 MP4 文件（不区分大小写）
        if path.lower().endswith(".mp4"):
            extract_audio_from_mp4(path, overwrite=overwrite)
        else:
            print(f"⏭️  跳过非 MP4 文件: {os.path.basename(path)}")
    elif os.path.isdir(path):
        print(f"📁 扫描目录: {path}")
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith(".mp4"):
                    full_path = os.path.join(root, file)
                    extract_audio_from_mp4(full_path, overwrite=overwrite)
    else:
        print(f"⚠️  未知类型: {path}")

# ------------------------------------------------------------
# 主程序入口
# ------------------------------------------------------------
def main():
    # 检查是否传入了文件/文件夹参数（拖放时会把所有路径作为参数）
    args = sys.argv[1:]  # 第一个是脚本自身
    if not args:
        print("使用方法:")
        print("  直接将 MP4 文件或文件夹拖到此程序图标上")
        print("  或在命令行中执行: mp4_to_mp3_drop.exe 文件1 文件夹1 ...")
        print("示例: mp4_to_mp3_drop.exe C:\\视频\\movie.mp4 D:\\我的视频")
        input("\n按 Enter 键退出...")
        return

    # 可选：是否强制覆盖已存在的 MP3（默认不覆盖）
    overwrite = False  # 可改为 True 或通过参数控制

    for arg in args:
        process_path(arg, overwrite=overwrite)

    print("\n🎉 所有任务处理完毕！")
    input("按 Enter 键退出...")

if __name__ == "__main__":
    main()