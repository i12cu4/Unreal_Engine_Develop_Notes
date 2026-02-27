"""
RAR压缩包解压图片
功能:处理指定目录下的所有rar文件，解压图片文件到目标目录，并显示进度条。
"""
import os
import subprocess
import tempfile
from tqdm import tqdm

# ===================== 用户配置区域 =====================
target_path = r"C:\Users\chru\Desktop\Task"
winrar_path = r"C:\Program File\WinRAR\Rar.exe"  # 请确保路径正确
# ======================================================

def process_rar_files(target_path, winrar_path):
    """
    处理指定目录下的所有rar文件，解压图片文件到目标目录，并显示进度条。
    """
    rar_files = [
        os.path.join(target_path, f)
        for f in os.listdir(target_path)
        if f.lower().endswith('.rar')
    ]

    with tqdm(rar_files, desc="处理压缩文件", unit="file") as pbar:
        for rar_file in pbar:
            pbar.set_postfix(file=os.path.basename(rar_file))
            
            # 检查是否已存在同名图片
            base_name = os.path.splitext(os.path.basename(rar_file))[0]
            found = False
            for ext in ['.png', '.jpg']:
                if os.path.exists(os.path.join(target_path, base_name + ext)):
                    found = True
                    break
            if found:
                pbar.write(f"跳过处理 {os.path.basename(rar_file)}，已存在同名图片")
                continue

            # 创建临时解压目录
            temp_dir = tempfile.mkdtemp(dir=target_path)
            try:
                # 获取压缩包文件列表
                list_cmd = [winrar_path, 'lb', rar_file]
                result = subprocess.run(list_cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    pbar.write(f"错误：无法列出 {rar_file} 的内容")
                    continue

                # 分析文件列表
                files = result.stdout.splitlines()
                image_file = None
                
                # 优先查找根目录图片
                for f in files:
                    if not ('/' in f or '\\' in f) and f.lower().endswith(('.jpg', '.png')):
                        image_file = f
                        break
                
                # 其次查找子目录图片
                if not image_file:
                    for f in files:
                        if ('/' in f or '\\' in f) and f.lower().endswith(('.jpg', '.png')):
                            image_file = f
                            break
                
                if not image_file:
                    pbar.write(f"未找到图片：{rar_file}")
                    continue

                # 解压文件到临时目录
                extract_cmd = [winrar_path, 'e', '-y', '-inul', 
                              rar_file, image_file, temp_dir]
                result = subprocess.run(extract_cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
                if result.returncode != 0:
                    pbar.write(f"解压失败：{rar_file} -> {image_file}")
                    continue

                # 处理解压后的文件
                src_name = os.path.basename(image_file)
                src_path = os.path.join(temp_dir, src_name)
                if not os.path.exists(src_path):
                    pbar.write(f"文件不存在：{src_path}")
                    continue

                # 生成目标文件名
                ext = os.path.splitext(image_file)[1].lower()
                dst_path = os.path.join(target_path, base_name + ext)
                
                # 移动并重命名文件
                try:
                    os.replace(src_path, dst_path)
                except Exception as e:
                    pbar.write(f"重命名失败：{src_path} -> {dst_path} ({e})")
            finally:
                # 清理临时目录
                try:
                    os.rmdir(temp_dir)
                except OSError:
                    import shutil
                    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    # 检查WinRAR是否存在
    if not os.path.exists(winrar_path):
        print(f"错误：WinRAR路径不存在 {winrar_path}")
        exit(1)
    
    # 运行处理程序
    process_rar_files(target_path, winrar_path)