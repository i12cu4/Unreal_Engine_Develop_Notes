#!/usr/bin/env python3
"""
酷狗公钥提取器 - 极度简化版本
仅生成一个包含KUGOU_KEY_XZ_HEX变量的.py文件
"""

import sys
from pathlib import Path

def main():
    """主函数"""
    
    # 查找kugou_key.xz文件
    search_paths = [
        Path.cwd() / "kugou_key.xz",
        Path.cwd() / "assets" / "kugou_key.xz",
        Path(__file__).parent / "kugou_key.xz",
        Path(__file__).parent / "assets" / "kugou_key.xz",
    ]
    
    xz_path = None
    for path in search_paths:
        if path.exists():
            xz_path = path
            print(f"找到文件: {xz_path}")
            break
    
    if not xz_path:
        print("错误: 未找到kugou_key.xz文件")
        print("请将文件放在以下位置之一:")
        for path in search_paths:
            print(f"  {path}")
        sys.exit(1)
    
    try:
        # 读取文件
        with open(xz_path, 'rb') as f:
            xz_data = f.read()
        
        # 转换为十六进制字符串
        hex_str = xz_data.hex()
        
        # 创建文件内容 - 仅包含变量定义
        file_content = f'KUGOU_KEY_XZ_HEX = "{hex_str}"'
        
        # 保存文件
        output_path = Path.cwd() / "kugou_key_simple.py"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"\n已生成: {output_path}")
        print(f"数据大小: {len(xz_data):,} 字节")
        print(f"十六进制长度: {len(hex_str):,} 字符")
        print("\n使用说明:")
        print("1. 打开生成的 kugou_key_simple.py 文件")
        print("2. 复制 KUGOU_KEY_XZ_HEX = \"...\" 整行内容")
        print("3. 粘贴到解密工具中的指定位置")
        
    except Exception as e:
        print(f"处理失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

