import subprocess
import os
import uuid
import sys
import re

FFMPEG_PATH = r"C:\Program File\ffmpeg\bin\ffmpeg.exe"
VIDEO_EXTS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v']

def sanitize_input(text):
    return text.strip().strip('"').strip("'")

def validate_filename(name):
    if any(c in name for c in '\\/:*?"<>|'):
        return False, '文件名包含非法字符（\\ / : * ? " < > |）'
    if os.path.dirname(name):
        return False, "请仅输入文件名，不要包含路径"
    if not name.strip():
        return False, "文件名不能为空"
    return True, ""

def find_video_in_folder(folder, raw_name):
    """智能匹配视频文件：支持无扩展名输入"""
    clean_name = sanitize_input(raw_name)
    
    # 1. 检查原样是否存在
    full_path = os.path.join(folder, clean_name)
    if os.path.isfile(full_path):
        return full_path, clean_name
    
    # 2. 尝试补全常见视频扩展名
    matches = []
    base_name = os.path.splitext(clean_name)[0]  # 移除用户可能误加的无效扩展名
    for ext in VIDEO_EXTS:
        candidate = base_name + ext
        candidate_path = os.path.join(folder, candidate)
        if os.path.isfile(candidate_path):
            matches.append((candidate, candidate_path))
    
    # 3. 处理匹配结果
    if not matches:
        return None, f"❌ 文件不存在: '{clean_name}'（已尝试常见视频扩展名）"
    if len(matches) > 1:
        msg = "⚠️  找到多个匹配文件:\n"
        for i, (name, _) in enumerate(matches, 1):
            msg += f"  {i}. {name}\n"
        msg += "请输入编号选择（0=取消）: "
        return "MULTIPLE", msg + "|" + "|".join([m[0] for m in matches])
    
    # 唯一匹配
    selected_name, selected_path = matches[0]
    print(f"ℹ️  自动补全文件名 → {selected_name}")
    return selected_path, selected_name

def get_valid_video_file(folder):
    while True:
        print("\n💡 提示：输入视频文件名（可省略.mp4等后缀），输入 'exit' 退出")
        raw = input("🎬 请输入视频文件名: ")
        if raw.strip().lower() in ['exit', 'quit', 'q']:
            print("\n👋 退出程序")
            sys.exit(0)
        
        result, info = find_video_in_folder(folder, raw)
        
        if result is None:  # 无匹配
            print(info)
            continue
        if result == "MULTIPLE":  # 多匹配
            parts = info.split('|')
            prompt = parts[0]
            candidates = parts[1:]
            print(prompt, end='')
            try:
                choice = int(input().strip())
                if choice == 0:
                    continue
                if 1 <= choice <= len(candidates):
                    sel_name = candidates[choice-1]
                    return os.path.join(folder, sel_name), sel_name
                else:
                    print("❌ 无效编号")
                    continue
            except:
                print("❌ 无效输入")
                continue
        
        # 唯一匹配或原样存在
        return result, info  # info此时是文件名

def get_clips_config():
    while True:
        try:
            n = int(input("\n✂️  请输入要裁剪的片段数量（1=单段，2+=多段拼接）: ").strip())
            if n < 1:
                print("❌ 请输入大于0的整数")
                continue
            break
        except ValueError:
            print("❌ 无效输入，请输入数字")
    
    clips = []
    print(f"\n⏱️  请依次输入 {n} 个片段的起始和结束时间（格式: 4:30 表示4分30秒）")
    for i in range(n):
        while True:
            start = input(f"  → 片段 {i+1} 起始时间: ").strip()
            end = input(f"  → 片段 {i+1} 结束时间: ").strip()
            if not re.match(r'^\d{1,3}(:\d{1,2}){0,2}(\.\d+)?$', start) or \
               not re.match(r'^\d{1,3}(:\d{1,2}){0,2}(\.\d+)?$', end):
                print("❌ 时间格式错误！请使用: 4:30 或 1:23:45")
                continue
            clips.append((start, end))
            break
    return clips

def process_video(video_path, clips, output_dir):
    uid = uuid.uuid4().hex[:8]
    temp_files = []
    
    try:
        if len(clips) == 1:
            temp_out = os.path.join(output_dir, f"temp_{uid}.mp4")
            # 修复核心：-ss 和 -to 必须在 -i 之前（输入选项）
            cmd = [
                FFMPEG_PATH,
                "-ss", clips[0][0],
                "-to", clips[0][1],  # 关键：绝对时间点（4分41秒）
                "-i", video_path,
                "-c", "copy",
                "-y",
                temp_out
            ]
            print(f"\n[⏳] 精确裁剪 {clips[0][0]} → {clips[0][1]} （严格输出中间内容）...")
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            final_temp = temp_out
            temp_files.append(temp_out)
            print("[✅] 单片段裁剪完成")
        else:
            clip_paths = []
            for i, (start, end) in enumerate(clips):
                temp_clip = os.path.join(output_dir, f"temp_{uid}_clip{i}.mp4")
                cmd = [
                    FFMPEG_PATH,
                    "-ss", start,
                    "-to", end,  # 关键修复：放在 -i 之前
                    "-i", video_path,
                    "-c", "copy",
                    "-y",
                    temp_clip
                ]
                print(f"[⏳] 裁剪片段 {i+1}/{len(clips)}: {start} → {end} ...")
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                clip_paths.append(temp_clip)
                temp_files.append(temp_clip)
            
            # 生成concat文件（加入清理列表）
            concat_txt = os.path.join(output_dir, f"concat_{uid}.txt")
            with open(concat_txt, 'w', encoding='utf-8') as f:
                for cp in clip_paths:
                    f.write(f"file '{os.path.abspath(cp).replace(chr(92), '/')}'\n")
            temp_files.append(concat_txt)  # 确保concat文件被记录
            
            merged_temp = os.path.join(output_dir, f"merged_{uid}.mp4")
            cmd = [
                FFMPEG_PATH, "-f", "concat", "-safe", "0", "-i", concat_txt,
                "-c", "copy", "-y", merged_temp
            ]
            print("[⏳] 拼接所有片段...")
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            final_temp = merged_temp
            temp_files.append(merged_temp)
            print("[✅] 多片段拼接完成")
        
        return final_temp, temp_files
    except subprocess.CalledProcessError:
        raise RuntimeError("ffmpeg处理失败（时间点可能无效/超出范围）")
    except Exception as e:
        raise RuntimeError(f"处理异常: {str(e)}")

def main():
    if not os.path.exists(FFMPEG_PATH):
        print(f"❌ 致命错误：ffmpeg.exe 不存在！")
        print(f"   路径: {FFMPEG_PATH}")
        sys.exit(1)
    
    print("=" * 60)
    print("🎬 视频精准裁剪工具（参数零修改 · 流拷贝模式）")
    print(f"🔧 ffmpeg路径: {FFMPEG_PATH}")
    print("💡 输入视频文件名时可省略.mp4等后缀 | 输入 'exit' 随时退出")
    print("=" * 60)
    
    # 获取素材文件夹（仅首次）
    while True:
        raw = input("📁 请输入素材文件夹路径: ")
        if raw.strip().lower() in ['exit', 'quit', 'q']:
            print("\n👋 退出程序")
            sys.exit(0)
        folder = sanitize_input(raw)
        if os.path.isdir(folder):
            material_folder = os.path.abspath(folder)
            break
        print(f"❌ 无效文件夹: {folder}")
    
    print(f"\n✅ 素材文件夹: {material_folder}")
    print("🔄 程序将循环处理该文件夹下的视频（自动进入下一轮）\n")
    
    # 主循环（无限循环，无确认提示）
    while True:
        temp_files = []  # 每轮初始化
        try:
            # 1. 获取视频文件（智能补全扩展名）
            video_path, video_name = get_valid_video_file(material_folder)
            print(f"✅ 处理视频: {video_name}")
            
            # 2. 获取裁剪参数
            clips = get_clips_config()
            
            # 3. 执行裁剪
            final_temp, temp_files = process_video(video_path, clips, material_folder)
            
            # 4. 生成带源文件前缀的输出文件名
            base_source = os.path.splitext(video_name)[0]  # 源文件名（不含扩展名）
            while True:
                raw_out = input("\n💾 请输入保存标识（如'haha'，将生成'源文件名_haha.mp4'）: ")
                clean_out = sanitize_input(raw_out)
                if clean_out.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 退出程序")
                    sys.exit(0)
                
                # 验证用户输入部分
                valid, msg = validate_filename(clean_out)
                if not valid:
                    print(f"❌ {msg}")
                    continue
                
                # 构建最终文件名：源文件名_用户输入.扩展名
                user_base, user_ext = os.path.splitext(clean_out)
                if not user_ext or user_ext == '.':
                    output_filename = f"{base_source}_{user_base}.mp4"
                else:
                    output_filename = f"{base_source}_{user_base}{user_ext}"
                
                # 验证组合后文件名
                valid_final, msg_final = validate_filename(output_filename)
                if not valid_final:
                    print(f"❌ 生成的文件名非法: {output_filename}")
                    continue
                
                output_path = os.path.join(material_folder, output_filename)
                
                # 覆盖确认
                if os.path.abspath(output_path).lower() == os.path.abspath(video_path).lower():
                    if input("⚠️  输出文件与源视频同名！确认覆盖? (y/n): ").lower() != 'y':
                        continue
                if os.path.exists(output_path):
                    if input(f"⚠️  '{output_filename}' 已存在，覆盖? (y/n): ").lower() != 'y':
                        continue
                
                # 保存文件
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(final_temp, output_path)
                print(f"\n[🎉] 成功！文件已保存至:\n{output_path}")
                break
            
            print("\n" + "-" * 60)
            print("✅ 本轮完成 → 自动进入下一轮处理...")
            print("-" * 60)
            
        except RuntimeError as e:
            print(f"\n❌ 处理失败: {e}")
            # 清理临时文件（异常时）
            for tf in temp_files:
                try:
                    if os.path.exists(tf):
                        os.remove(tf)
                except:
                    pass
            print("👉 检查时间点是否有效（起始<结束）")
            continue
        except KeyboardInterrupt:
            print("\n\n⚠️  操作被中断")
            for tf in temp_files:
                try:
                    if os.path.exists(tf):
                        os.remove(tf)
                except:
                    pass
            continue
        finally:
            # 确保所有临时文件被清理（包括concat文件）
            for tf in temp_files:
                try:
                    if os.path.exists(tf):
                        os.remove(tf)
                except:
                    pass

if __name__ == "__main__":
    main()