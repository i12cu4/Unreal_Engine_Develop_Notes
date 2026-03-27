import sys
import os
import subprocess
import re
import uuid

# ================== 配置区 ==================
FFMPEG_PATH = r"C:\Program File\ffmpeg\bin\ffmpeg.exe"  # 请按实际路径修改
VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
ILLEGAL_CHARS = r'\/:*?"<>|'  # Windows文件名非法字符
# ===========================================

def parse_time_to_seconds(time_str):
    """将时间字符串转为总秒数（支持 0:31 / 1:23:45.5）"""
    parts = time_str.strip().split(':')
    if len(parts) > 3:
        raise ValueError("时间部分过多（最多3段：时:分:秒）")
    try:
        if len(parts) == 3:
            h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = int(parts[0]), float(parts[1])
            return m * 60 + s
        else:
            return float(parts[0])
    except (ValueError, IndexError):
        raise ValueError("时间格式解析失败")

def format_time_for_filename(time_str):
    """生成4位时间字符串（四舍五入到整秒，格式：MMSS）"""
    total_sec = parse_time_to_seconds(time_str)
    total_sec_int = round(total_sec)
    minutes = total_sec_int // 60
    seconds = total_sec_int % 60
    if minutes >= 100:
        raise ValueError("时间超过99分钟，无法生成标准文件名")
    return f"{minutes:02d}{seconds:02d}"

def validate_video_path(path):
    """校验拖入的文件是否为有效视频"""
    if not os.path.isfile(path):
        return False, f"文件不存在: {path}"
    _, ext = os.path.splitext(path)
    if ext.lower() not in VIDEO_EXTS:
        return False, f"非视频文件（需为{', '.join(VIDEO_EXTS)}）: {path}"
    return True, ""

def validate_suffix(suffix):
    """校验附加标识：空字符串合法；非空需不含非法字符"""
    if not suffix:
        return True, ""
    if any(c in suffix for c in ILLEGAL_CHARS):
        illegal_found = [c for c in ILLEGAL_CHARS if c in suffix]
        return False, f"包含非法字符: {' '.join(repr(c) for c in illegal_found)}"
    return True, ""

def main():
    # ========== 启动校验 ==========
    if not os.path.exists(FFMPEG_PATH):
        print(f"❌ 致命错误：ffmpeg.exe 未找到！\n请修改代码顶部 FFMPEG_PATH 为实际路径")
        print(f"当前配置路径: {FFMPEG_PATH}")
        sys.exit(1)
    
    if len(sys.argv) != 2:
        print("❌ 错误：请拖动【单个】视频文件到本程序图标上运行")
        print("（不支持多选/文件夹/无参数启动）")
        sys.exit(1)
    
    video_path = sys.argv[1]
    is_valid, msg = validate_video_path(video_path)
    if not is_valid:
        print(f"❌ {msg}")
        sys.exit(1)
    
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = os.path.dirname(video_path)
    print("=" * 60)
    print(f"🎬 正在处理: {os.path.basename(video_path)}")
    print(f"📍 输出目录: {output_dir}")
    print("💡 输入裁剪时间（格式: 0:31）| 附加标识留空则无后缀 | Ctrl+C 退出")
    print("=" * 60)

    # ========== 死循环裁剪 ==========
    while True:
        try:
            # 输入时间
            start_raw = input("\n✂️  起始时间: ").strip()
            end_raw = input("✂️  结束时间: ").strip()
            
            # 格式粗校验
            time_pattern = r'^\d{1,3}(:\d{1,2}){0,2}(\.\d+)?$'
            if not re.match(time_pattern, start_raw) or not re.match(time_pattern, end_raw):
                print("❌ 时间格式错误！示例: 0:31 或 1:23:45")
                continue
            
            # 精确校验与转换
            try:
                start_sec = parse_time_to_seconds(start_raw)
                end_sec = parse_time_to_seconds(end_raw)
                if start_sec >= end_sec:
                    print("❌ 起始时间必须小于结束时间")
                    continue
                start_tag = format_time_for_filename(start_raw)
                end_tag = format_time_for_filename(end_raw)
            except ValueError as e:
                print(f"❌ {e}")
                continue
            
            # 输入附加标识（带校验循环）
            while True:
                suffix_raw = input("🔖 附加标识（留空则无）: ").strip()
                is_valid_suffix, err_msg = validate_suffix(suffix_raw)
                if not is_valid_suffix:
                    print(f"❌ {err_msg}（禁止字符: \\ / : * ? \" < > |）")
                    continue
                suffix_clean = suffix_raw  # 已strip，空字符串即无标识
                break
            
            # 生成文件名
            if suffix_clean:
                output_filename = f"{base_name}_{start_tag}_{end_tag}_{suffix_clean}.mp4"
            else:
                output_filename = f"{base_name}_{start_tag}_{end_tag}.mp4"
            
            # 防覆盖源文件
            output_path = os.path.join(output_dir, output_filename)
            if os.path.abspath(output_path).lower() == os.path.abspath(video_path).lower():
                print(f"⚠️  跳过：输出文件名与源视频冲突（{output_filename}），请调整时间或标识")
                continue
            
            # 执行裁剪
            temp_file = os.path.join(output_dir, f"temp_{uuid.uuid4().hex[:8]}.mp4")
            cmd = [
                FFMPEG_PATH,
                "-ss", start_raw,
                "-to", end_raw,
                "-i", video_path,
                "-c", "copy",
                "-y",
                temp_file
            ]
            print(f"[⏳] 裁剪 {start_raw} → {end_raw} ...")
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            
            # 保存结果（覆盖同名文件无询问）
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_file, output_path)
            print(f"[✅] 已保存: {output_filename}")
            
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 检测到中断，程序退出")
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.decode('utf-8', errors='ignore').strip() if e.stderr else "未知错误"
            print(f"❌ ffmpeg执行失败: {err_msg[:200]}")
            if 'temp_file' in locals() and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        except Exception as e:
            print(f"❌ 系统错误: {str(e)}")
            if 'temp_file' in locals() and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

if __name__ == "__main__":
    main()