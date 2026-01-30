import os
import sys
import subprocess
import json
from pathlib import Path
import threading
from queue import Queue

def check_ffmpeg():
    """检查FFmpeg是否可用"""
    # 尝试用户指定的路径
    user_ffmpeg_path = r"C:\Program File\ffmpeg\bin\ffmpeg.exe"
    
    # 检查常见路径
    common_paths = [
        user_ffmpeg_path,
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\ffmpeg.exe",
        r"C:\ffmpeg\ffmpeg.exe"
    ]
    
    # 检查系统PATH中的ffmpeg
    try:
        # 使用二进制模式避免编码问题
        result = subprocess.run(['ffmpeg', '-version'], 
                               capture_output=True, 
                               check=True)
        print("✓ 系统PATH中找到FFmpeg")
        return "ffmpeg"  # 使用系统命令
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # 检查指定路径
    for path in common_paths:
        if os.path.exists(path):
            print(f"✓ 找到FFmpeg: {path}")
            return path
    
    # 所有路径都未找到
    print("✗ 未找到FFmpeg。请确保FFmpeg已正确安装。")
    print("建议安装路径：")
    for path in common_paths:
        print(f"  - {path}")
    return None

def get_mp4_files(folder_path):
    """获取文件夹中所有mp4文件"""
    if not os.path.exists(folder_path):
        return []
    
    mp4_files = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.mp4'):
            mp4_files.append(filename)
    return mp4_files

def convert_mp4_to_mp3(ffmpeg_path, video_path, output_path):
    """使用ffmpeg将mp4转换为mp3，修复编码问题"""
    try:
        # 构建ffmpeg命令
        command = [
            ffmpeg_path,
            '-i', video_path,
            '-vn',  # 不处理视频流
            '-acodec', 'libmp3lame',  # 使用mp3编码器
            '-q:a', '2',  # 音频质量 (2是高质量)
            '-y',  # 覆盖已存在的文件
            output_path
        ]
        
        print("  执行命令: " + " ".join(command))
        
        # 使用二进制模式执行命令，避免编码问题
        # 不捕获输出，直接显示在控制台
        result = subprocess.run(command, 
                               check=True,
                               stderr=subprocess.DEVNULL,  # 隐藏错误输出
                               stdout=subprocess.DEVNULL)  # 隐藏标准输出
        
        return True, None
    except subprocess.CalledProcessError as e:
        return False, f"FFmpeg执行失败，返回码: {e.returncode}"
    except Exception as e:
        return False, f"转换过程出错: {str(e)}"

def main():
    """主函数"""
    print("=" * 60)
    print("MP4 转 MP3 音频提取工具 (稳定版)")
    print("=" * 60)
    
    # 检查FFmpeg
    ffmpeg_path = check_ffmpeg()
    if not ffmpeg_path:
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 设置文件夹路径
    desktop_path = str(Path.home() / "Desktop")
    default_folder = os.path.join(desktop_path, "mp4_to_mp3")
    
    print(f"\n【文件夹设置】")
    print(f"请指定包含MP4文件的文件夹路径")
    print(f"默认路径: {default_folder}")
    
    folder_path = input("\n输入文件夹路径 (直接按回车使用默认路径): ").strip()
    
    if not folder_path:
        folder_path = default_folder
        # 如果默认文件夹不存在，尝试创建
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                print(f"\n✓ 已创建默认文件夹: {folder_path}")
                print("请将MP4文件放入此文件夹后重新运行程序")
                input("\n按回车键退出...")
                sys.exit(0)
            except Exception as e:
                print(f"\n✗ 无法创建默认文件夹: {str(e)}")
                folder_path = desktop_path
    
    # 确保路径使用正确的分隔符
    folder_path = os.path.normpath(folder_path)
    print(f"\n✓ 使用文件夹路径: {folder_path}")
    
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"\n✗ 文件夹不存在: {folder_path}")
        create = input("是否创建此文件夹? (y/n): ").lower().strip()
        if create == 'y':
            try:
                os.makedirs(folder_path)
                print(f"\n✓ 已创建文件夹: {folder_path}")
                print("请将MP4文件放入此文件夹后重新运行程序")
                input("\n按回车键退出...")
                sys.exit(0)
            except Exception as e:
                print(f"\n✗ 创建文件夹失败: {str(e)}")
                input("\n按回车键退出...")
                sys.exit(1)
        else:
            input("\n按回车键退出...")
            sys.exit(1)
    
    # 获取MP4文件
    mp4_files = get_mp4_files(folder_path)
    
    if not mp4_files:
        print(f"\n⚠ 在文件夹中未找到任何MP4文件")
        print("请确保文件夹中包含 .mp4 文件")
        print("\n提示：你可以将MP4文件拖放到此窗口中，然后按回车键")
        input("\n按回车键退出...")
        sys.exit(0)
    
    print(f"\n【文件列表】")
    print(f"找到 {len(mp4_files)} 个MP4文件:")
    for i, file in enumerate(mp4_files, 1):
        try:
            file_size = os.path.getsize(os.path.join(folder_path, file)) / (1024 * 1024)
            print(f"  {i:2d}. {file} ({file_size:.2f} MB)")
        except:
            print(f"  {i:2d}. {file}")
    
    confirm = input("\n确认转换这些文件? (y/n): ").lower().strip()
    if confirm != 'y':
        print("\n操作已取消")
        input("\n按回车键退出...")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("开始转换进程")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    # 处理每个文件
    for i, filename in enumerate(mp4_files, 1):
        video_path = os.path.join(folder_path, filename)
        mp3_filename = os.path.splitext(filename)[0] + '.mp3'
        mp3_path = os.path.join(folder_path, mp3_filename)
        
        print(f"\n[{i}/{len(mp4_files)}] {'='*40}")
        print(f"处理文件: {filename}")
        
        # 检查文件大小
        try:
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"  文件大小: {file_size:.2f} MB")
        except Exception as e:
            print(f"  获取文件大小失败: {str(e)}")
        
        # 跳过已存在的MP3文件
        if os.path.exists(mp3_path):
            print(f"  ⚠ 跳过: {mp3_filename} 已存在")
            continue
        
        # 执行转换
        print("  正在转换音频，请稍候...")
        success, error = convert_mp4_to_mp3(ffmpeg_path, video_path, mp3_path)
        
        if success:
            if os.path.exists(mp3_path):
                try:
                    output_size = os.path.getsize(mp3_path) / (1024 * 1024)  # MB
                    print(f"  ✓ 转换成功: {mp3_filename} ({output_size:.2f} MB)")
                    success_count += 1
                except:
                    print(f"  ✓ 转换成功: {mp3_filename}")
                    success_count += 1
            else:
                print(f"  ✗ 转换失败: 输出文件不存在")
                fail_count += 1
        else:
            print(f"  ✗ 转换失败: {error}")
            fail_count += 1
    
    print("\n" + "=" * 60)
    print("转换结果汇总")
    print("=" * 60)
    print(f"成功转换: {success_count} 个文件")
    print(f"转换失败: {fail_count} 个文件")
    print(f"总处理数: {len(mp4_files)} 个文件")
    
    if success_count > 0:
        print(f"\n✓ 转换完成! MP3文件已保存到: {folder_path}")
        # 显示前3个成功转换的文件
        converted_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
        if converted_files:
            print("\n已转换的文件示例:")
            for i, file in enumerate(converted_files[:3], 1):
                print(f"  {i}. {file}")
            if len(converted_files) > 3:
                print(f"  ... 等 {len(converted_files)} 个文件")
    else:
        print("\n✗ 所有文件转换失败，请检查错误信息")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        input("\n按回车键退出...")
    except Exception as e:
        print(f"\n\n发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")