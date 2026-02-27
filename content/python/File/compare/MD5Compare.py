import hashlib
import os
import time

def calculate_md5(file_path, chunk_size=8192):
    """
    计算大文件的MD5哈希值，使用分块读取以避免内存问题
    
    Args:
        file_path (str): 文件的绝对路径
        chunk_size (int): 每次读取的块大小(字节)
    
    Returns:
        str: 文件的MD5哈希值
    """
    md5_hash = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # 初始化进度变量
            file_size = os.path.getsize(file_path)
            processed = 0
            start_time = time.time()
            
            # 分块读取文件并更新哈希
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(chunk)
                processed += len(chunk)
                
                # 每处理1GB显示一次进度
                if processed % (1024*1024*1024) < chunk_size:
                    elapsed = time.time() - start_time
                    speed = processed / (1024*1024*elapsed) if elapsed > 0 else 0
                    print(f"{file_path}: 已处理 {processed/(1024*1024*1024):.2f} GB / "
                          f"{file_size/(1024*1024*1024):.2f} GB, "
                          f"速度: {speed:.2f} MB/s")
                    
    except FileNotFoundError:
        print(f"错误: 文件不存在 {file_path}")
        return None
    except IOError:
        print(f"错误: 无法读取文件 {file_path}")
        return None
        
    return md5_hash.hexdigest()

def main():
    # 使用变量存储文件的绝对路径
    file1_path = r"E:\Download\ProjectsCity.rar"  # 请替换为第一个文件的实际路径
    file2_path = r"E:\Download\The Projects – Modular City Pack.rar"  # 请替换为第二个文件的实际路径
    
    print("开始计算第一个文件的MD5...")
    md5_file1 = calculate_md5(file1_path)
    
    if md5_file1 is None:
        return
    
    print("\n开始计算第二个文件的MD5...")
    md5_file2 = calculate_md5(file2_path)
    
    if md5_file2 is None:
        return
    
    print("\nMD5比较结果:")
    print(f"文件1: {md5_file1}")
    print(f"文件2: {md5_file2}")
    
    if md5_file1 == md5_file2:
        print("✅ 两个文件完全相同")
    else:
        print("❌ 两个文件不同")

if __name__ == "__main__":
    main()