import sys
import os
import subprocess
import datetime
import uuid
import re

# ================== 配置区 ==================
FFMPEG_PATH = r"C:\Program File\ffmpeg\bin\ffmpeg.exe"  # 请按实际路径修改
VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
# ===========================================

def validate_video_path(path):
    """校验文件是否为有效视频"""
    if not os.path.isfile(path):
        return False, f"文件不存在: {path}"
    _, ext = os.path.splitext(path)
    if ext.lower() not in VIDEO_EXTS:
        return False, f"非视频文件（支持格式: {', '.join(VIDEO_EXTS)}）"
    return True, ""

def clean_path_input(raw_input):
    """清理用户输入的路径：去除首尾空格/引号"""
    return raw_input.strip().strip('"').strip("'").strip()

def main():
    # ========== 启动校验 ==========
    if not os.path.exists(FFMPEG_PATH):
        print(f"❌ 致命错误：ffmpeg.exe 未找到！\n请修改代码顶部 FFMPEG_PATH 为实际路径")
        print(f"当前配置路径: {FFMPEG_PATH}")
        sys.exit(1)
    
    if len(sys.argv) != 2:
        print("❌ 错误：请拖动【单个】视频文件到本程序图标上启动")
        print("（必须且只能拖入一个视频作为起始文件）")
        sys.exit(1)
    
    first_video = sys.argv[1]
    is_valid, msg = validate_video_path(first_video)
    if not is_valid:
        print(f"❌ {msg}")
        sys.exit(1)
    
    video_list = [os.path.abspath(first_video)]
    base_dir = os.path.dirname(first_video)
    
    print("=" * 60)
    print(f"🎬 合并模式已启动 | 起始视频: {os.path.basename(first_video)}")
    print(f"📍 输出目录: {base_dir}")
    print("💡 请将【下一个】视频文件拖入此窗口（或输入路径），按回车确认")
    print("💡 输入空行（直接回车）即开始合并所有已添加视频")
    print("=" * 60)
    
    # ========== 收集视频列表 ==========
    while True:
        try:
            user_input = input("\n📎 拖入下一个视频（或回车结束添加）: ")
            cleaned = clean_path_input(user_input)
            
            if not cleaned:  # 空输入 → 结束收集
                if len(video_list) < 2:
                    print("⚠️  至少需要2个视频才能合并！请继续添加")
                    continue
                break
            
            # 验证新视频
            is_valid, msg = validate_video_path(cleaned)
            if not is_valid:
                print(f"❌ {msg} | 路径: {cleaned}")
                continue
            
            abs_path = os.path.abspath(cleaned)
            if abs_path in video_list:
                print(f"⚠️  跳过重复文件: {os.path.basename(cleaned)}")
                continue
            
            video_list.append(abs_path)
            print(f"✅ 已添加 ({len(video_list)}): {os.path.basename(cleaned)}")
            
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 检测到中断，程序退出")
            sys.exit(0)
    
    # ========== 生成合并列表文件 ==========
    list_file = os.path.join(base_dir, f"merge_list_{uuid.uuid4().hex[:8]}.txt")
    try:
        with open(list_file, 'w', encoding='utf-8') as f:
            for vid in video_list:
                # 路径标准化：反斜杠→正斜杠，避免ffmpeg解析问题
                safe_path = os.path.abspath(vid).replace('\\', '/')
                # 转义路径中的单引号（罕见但需防护）
                safe_path = safe_path.replace("'", r"\'")
                f.write(f"file '{safe_path}'\n")
        
        # ========== 执行合并 ==========
        output_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".mp4"
        output_path = os.path.join(base_dir, output_name)
        
        cmd = [
            FFMPEG_PATH,
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",  # 无损流拷贝，保持原始画质/音质
            "-y",
            output_path
        ]
        
        print("\n" + "=" * 60)
        print(f"🔧 开始合并 {len(video_list)} 个视频（无损模式）...")
        print(f"💾 输出文件: {output_name}")
        print("=" * 60)
        
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        
        print("\n✅ 合并成功！文件已保存至:")
        print(f"   {output_path}")
        print(f"\n📌 共处理 {len(video_list)} 个视频 | 无重新编码 | 画质零损失")
        
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode('utf-8', errors='ignore').strip() if e.stderr else "未知错误"
        print(f"\n❌ ffmpeg合并失败:")
        print(f"   错误摘要: {err_msg[:300]}")
        print("\n💡 常见原因：视频编码参数不一致（分辨率/帧率/编码器等）")
        print("   建议：使用相同来源或参数一致的视频进行合并")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 系统错误: {str(e)}")
        sys.exit(1)
    finally:
        # 清理临时列表文件
        if os.path.exists(list_file):
            try:
                os.remove(list_file)
            except:
                pass

if __name__ == "__main__":
    main()