import os
import sys
import subprocess

def rename_kgm_flac_to_kgm(file_path):
    """将 .kgm.flac 文件重命名为 .kgm 文件"""
    if file_path.endswith('.kgm.flac'):
        # 构建新文件名：去掉 .flac 后缀
        new_file_path = file_path[:-5]  # 去掉最后的 .flac (5个字符)
        
        # 检查新文件是否已存在（避免覆盖）
        if not os.path.exists(new_file_path):
            try:
                os.rename(file_path, new_file_path)
                print(f"已重命名: {os.path.basename(file_path)} -> {os.path.basename(new_file_path)}")
                return new_file_path
            except Exception as e:
                print(f"重命名失败 {file_path}: {e}")
        else:
            print(f"目标文件已存在，跳过重命名: {new_file_path}")
            return new_file_path
    return None

def collect_kgm_files(paths):
    """收集所有需要处理的 .kgm 文件路径"""
    kgm_files = []
    
    for path in paths:
        if not os.path.exists(path):
            print(f"路径不存在，跳过: {path}")
            continue
            
        if os.path.isfile(path):
            # 如果是 .kgm.flac 文件，先重命名
            if path.endswith('.kgm.flac'):
                kgm_path = rename_kgm_flac_to_kgm(path)
                if kgm_path and kgm_path.endswith('.kgm'):
                    kgm_files.append(kgm_path)
            # 如果是 .kgm 文件，直接添加到列表
            elif path.endswith('.kgm'):
                kgm_files.append(path)
                
        elif os.path.isdir(path):
            # 递归遍历文件夹
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 处理 .kgm.flac 文件
                    if file.endswith('.kgm.flac'):
                        kgm_path = rename_kgm_flac_to_kgm(file_path)
                        if kgm_path and kgm_path.endswith('.kgm'):
                            kgm_files.append(kgm_path)
                    # 处理 .kgm 文件
                    elif file.endswith('.kgm'):
                        kgm_files.append(file_path)
    
    return kgm_files

def convert_kgm_to_mp3(kgm_files):
    """使用 kgm2mp3.exe 转换 .kgm 文件为 .mp3"""
    exe_path = os.path.join(os.path.dirname(__file__), "kgm2mp3.exe")
    
    if not os.path.exists(exe_path):
        print(f"错误: 找不到 kgm2mp3.exe 文件，请确保它和本程序在同一目录下")
        return False
    
    print(f"找到 kgm2mp3.exe: {exe_path}")
    print(f"开始转换 {len(kgm_files)} 个 .kgm 文件...")
    
    converted_count = 0
    skipped_count = 0
    
    for kgm_file in kgm_files:
        # 检查对应的 .mp3 文件是否已存在
        mp3_file = kgm_file.rsplit('.', 1)[0] + '.mp3'
        
        if os.path.exists(mp3_file):
            print(f"MP3文件已存在，跳过转换: {os.path.basename(kgm_file)}")
            skipped_count += 1
            continue
        
        # 转换文件
        try:
            print(f"正在转换: {os.path.basename(kgm_file)}")
            
            # 使用 subprocess.Popen 替代 subprocess.run 来避免线程问题
            cmd = f'"{exe_path}" "{kgm_file}"'
            process = subprocess.Popen(
                cmd, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'  # 忽略编码错误
            )
            
            # 等待进程完成
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                print(f"转换成功: {os.path.basename(kgm_file)}")
                converted_count += 1
            else:
                if stderr:
                    print(f"转换失败 {os.path.basename(kgm_file)}: {stderr.strip()}")
                else:
                    print(f"转换失败 {os.path.basename(kgm_file)}: 未知错误")
                
        except Exception as e:
            print(f"转换异常 {os.path.basename(kgm_file)}: {e}")
    
    print(f"转换完成: 成功 {converted_count} 个，跳过 {skipped_count} 个")
    return converted_count > 0 or skipped_count > 0

def delete_kgm_files(kgm_files):
    """删除所有 .kgm 文件"""
    if not kgm_files:
        print("没有需要删除的 .kgm 文件")
        return
    
    print(f"开始删除 {len(kgm_files)} 个 .kgm 文件...")
    deleted_count = 0
    
    for kgm_file in kgm_files:
        try:
            os.remove(kgm_file)
            print(f"已删除: {os.path.basename(kgm_file)}")
            deleted_count += 1
        except Exception as e:
            print(f"删除失败 {kgm_file}: {e}")
    
    print(f"删除完成: 成功删除 {deleted_count} 个 .kgm 文件")

def process_paths(paths):
    """主处理函数"""
    if not paths:
        print("请将文件或文件夹拖拽到本程序")
        input("按回车键退出...")
        return
    
    print(f"开始处理 {len(paths)} 个路径...")
    print("-" * 50)
    
    # 步骤1: 收集所有 .kgm 文件（包括重命名后的）
    print("步骤1: 收集和处理 .kgm.flac 文件")
    kgm_files = collect_kgm_files(paths)
    
    if not kgm_files:
        print("未找到任何 .kgm 或 .kgm.flac 文件")
        input("按回车键退出...")
        return
    
    print(f"找到 {len(kgm_files)} 个 .kgm 文件")
    print("-" * 50)
    
    # 步骤2: 转换 .kgm 文件为 .mp3
    print("步骤2: 转换 .kgm 文件为 .mp3")
    conversion_done = convert_kgm_to_mp3(kgm_files)
    
    if conversion_done:
        print("-" * 50)
        
        # 步骤3: 删除所有 .kgm 文件
        print("步骤3: 删除所有 .kgm 文件")
        delete_kgm_files(kgm_files)
    
    print("-" * 50)
    print("处理完成!")
    input("按回车键退出...")

def main():
    """主函数入口"""
    # 获取拖拽到程序的路径
    paths = sys.argv[1:]
    
    # 启动处理
    process_paths(paths)

if __name__ == "__main__":
    main()