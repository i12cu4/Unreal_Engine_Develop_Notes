import sys
import os

def compare_files(file1_path, file2_path):
    """比对两个文件的字节差异"""
    try:
        with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
            data1 = f1.read()
            data2 = f2.read()
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return False
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return False
    
    len1 = len(data1)
    len2 = len(data2)
    
    print("=" * 60)
    print("文件比对工具")
    print("=" * 60)
    print(f"文件1: {os.path.basename(file1_path)} ({len1:,} 字节)")
    print(f"文件2: {os.path.basename(file2_path)} ({len2:,} 字节)")
    print("-" * 50)
    
    # 检查文件是否完全相同
    if data1 == data2:
        print("✅ 两个文件完全相同")
        print(f"文件大小: {len1:,} 字节")
        return True
    
    # 检查文件大小差异
    if len1 != len2:
        print(f"⚠️  文件大小不同: 文件1={len1:,} 字节, 文件2={len2:,} 字节")
        print(f"   大小差异: {abs(len1-len2):,} 字节")
    
    # 计算差异
    diff_count = 0
    max_len = max(len1, len2)
    first_diff_pos = -1
    diff_bytes_hex = []
    
    for i in range(max_len):
        byte1 = data1[i] if i < len1 else None
        byte2 = data2[i] if i < len2 else None
        
        if byte1 != byte2:
            diff_count += 1
            if first_diff_pos == -1:
                first_diff_pos = i
                # 记录前几个差异字节（最多5个）
                diff_bytes_hex.append((i, byte1, byte2))
            elif len(diff_bytes_hex) < 5:
                diff_bytes_hex.append((i, byte1, byte2))
    
    # 输出差异信息
    print(f"差异统计:")
    print(f"  总字节数: {max_len:,}")
    print(f"  差异字节数: {diff_count:,}")
    print(f"  相同字节数: {max_len - diff_count:,}")
    print(f"  差异率: {diff_count/max_len*100:.2f}%")
    
    if diff_count > 0 and diff_bytes_hex:
        print(f"\n第一个差异在位置: 0x{first_diff_pos:08X} (十进制: {first_diff_pos})")
        print("前几个差异字节:")
        for i, byte1, byte2 in diff_bytes_hex:
            if byte1 is None:
                print(f"  位置 0x{i:08X}: 文件1: -- 文件2: {byte2:02X} ({chr(byte2) if 32 <= byte2 < 127 else '.'})")
            elif byte2 is None:
                print(f"  位置 0x{i:08X}: 文件1: {byte1:02X} ({chr(byte1) if 32 <= byte1 < 127 else '.'}) 文件2: --")
            else:
                print(f"  位置 0x{i:08X}: 文件1: {byte1:02X} ({chr(byte1) if 32 <= byte1 < 127 else '.'}) 文件2: {byte2:02X} ({chr(byte2) if 32 <= byte2 < 127 else '.'})")
    
    if diff_count > 5:
        print(f"\n注: 共发现 {diff_count:,} 个差异，只显示了前5个差异位置")
    
    return False

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("使用方法：")
        print("1. 将两个要比对的文件拖放到此脚本上")
        print("2. 或使用命令行: python script.py 文件1 文件2")
        print("")
        print("示例：")
        print('  python compare.py "C:\\文件1.kgm" "C:\\文件2.flac"')
        print("")
        input("按回车键退出...")
        return
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    # 验证文件是否存在
    if not os.path.exists(file1):
        print(f"错误: 文件1不存在 - {file1}")
        return
    
    if not os.path.exists(file2):
        print(f"错误: 文件2不存在 - {file2}")
        return
    
    # 比对文件
    compare_files(file1, file2)
    
    print("\n" + "=" * 60)
    input("按回车键退出...")

if __name__ == "__main__":
    main()