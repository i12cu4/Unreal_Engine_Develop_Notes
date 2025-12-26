#!/usr/bin/env python3
"""
酷狗音乐解密工具
"""

import sys
import lzma
import io
from pathlib import Path

# ================================================
# 请在这里粘贴您的密钥数据
# ================================================

KUGOU_KEY_XZ_HEX = ""  # 请将密钥粘贴在此处（与解密工具相同）

# ================================================

class KuGouDecoder:
    """酷狗音乐解密器"""
    
    # 常量定义
    HEADER_LEN = 1024  # 酷狗文件头固定长度
    OWN_KEY_LEN = 17   # 私钥长度（实际使用16个字节）
    PUB_KEY_LEN_MAGNIFICATION = 16  # 公钥索引放大倍数
    
    # 酷狗文件魔数（28字节）
    MAGIC_HEADER = bytes([
        0x7c, 0xd5, 0x32, 0xeb, 0x86, 0x02, 0x7f, 0x4b, 0xa8, 0xaf, 0xa6, 0x8e, 0x0f, 0xff, 0x99,
        0x14, 0x00, 0x04, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00
    ])
    
    # 公钥修正表（272字节）
    PUB_KEY_MEND = bytes([
        0xB8, 0xD5, 0x3D, 0xB2, 0xE9, 0xAF, 0x78, 0x8C, 0x83, 0x33, 0x71, 0x51, 0x76, 0xA0,
        0xCD, 0x37, 0x2F, 0x3E, 0x35, 0x8D, 0xA9, 0xBE, 0x98, 0xB7, 0xE7, 0x8C, 0x22, 0xCE,
        0x5A, 0x61, 0xDF, 0x68, 0x69, 0x89, 0xFE, 0xA5, 0xB6, 0xDE, 0xA9, 0x77, 0xFC, 0xC8,
        0xBD, 0xBD, 0xE5, 0x6D, 0x3E, 0x5A, 0x36, 0xEF, 0x69, 0x4E, 0xBE, 0xE1, 0xE9, 0x66,
        0x1C, 0xF3, 0xD9, 0x02, 0xB6, 0xF2, 0x12, 0x9B, 0x44, 0xD0, 0x6F, 0xB9, 0x35, 0x89,
        0xB6, 0x46, 0x6D, 0x73, 0x82, 0x06, 0x69, 0xC1, 0xED, 0xD7, 0x85, 0xC2, 0x30, 0xDF,
        0xA2, 0x62, 0xBE, 0x79, 0x2D, 0x62, 0x62, 0x3D, 0x0D, 0x7E, 0xBE, 0x48, 0x89, 0x23,
        0x02, 0xA0, 0xE4, 0xD5, 0x75, 0x51, 0x32, 0x02, 0x53, 0xFD, 0x16, 0x3A, 0x21, 0x3B,
        0x16, 0x0F, 0xC3, 0xB2, 0xBB, 0xB3, 0xE2, 0xBA, 0x3A, 0x3D, 0x13, 0xEC, 0xF6, 0x01,
        0x45, 0x84, 0xA5, 0x70, 0x0F, 0x93, 0x49, 0x0C, 0x64, 0xCD, 0x31, 0xD5, 0xCC, 0x4C,
        0x07, 0x01, 0x9E, 0x00, 0x1A, 0x23, 0x90, 0xBF, 0x88, 0x1E, 0x3B, 0xAB, 0xA6, 0x3E,
        0xC4, 0x73, 0x47, 0x10, 0x7E, 0x3B, 0x5E, 0xBC, 0xE3, 0x00, 0x84, 0xFF, 0x09, 0xD4,
        0xE0, 0x89, 0x0F, 0x5B, 0x58, 0x70, 0x4F, 0xFB, 0x65, 0xD8, 0x5C, 0x53, 0x1B, 0xD3,
        0xC8, 0xC6, 0xBF, 0xEF, 0x98, 0xB0, 0x50, 0x4F, 0x0F, 0xEA, 0xE5, 0x83, 0x58, 0x8C,
        0x28, 0x2C, 0x84, 0x67, 0xCD, 0xD0, 0x9E, 0x47, 0xDB, 0x27, 0x50, 0xCA, 0xF4, 0x63,
        0x63, 0xE8, 0x97, 0x7F, 0x1B, 0x4B, 0x0C, 0xC2, 0xC1, 0x21, 0x4C, 0xCC, 0x58, 0xF5,
        0x94, 0x52, 0xA3, 0xF3, 0xD3, 0xE0, 0x68, 0xF4, 0x00, 0x23, 0xF3, 0x5E, 0x0A, 0x7B,
        0x93, 0xDD, 0xAB, 0x12, 0xB2, 0x13, 0xE8, 0x84, 0xD7, 0xA7, 0x9F, 0x0F, 0x32, 0x4C,
        0x55, 0x1D, 0x04, 0x36, 0x52, 0xDC, 0x03, 0xF3, 0xF9, 0x4E, 0x42, 0xE9, 0x3D, 0x61,
        0xEF, 0x7C, 0xB6, 0xB3, 0x93, 0x50
    ])
    
    def __init__(self, input_file):
        """初始化解密器"""
        self.input_file = input_file
        self.own_key = bytearray(self.OWN_KEY_LEN)
        self.pos = 0  # 当前读取位置（从加密数据开始处计算）
        self._pub_key_data = None
        
        # 读取文件头并验证
        if not self._read_and_validate_header():
            raise ValueError("文件格式错误：不是有效的酷狗加密文件")

    def _read_and_validate_header(self):
        """读取并验证文件头"""
        # 读取1024字节的文件头
        header = self.input_file.read(self.HEADER_LEN)
        if len(header) < self.HEADER_LEN:
            return False
        
        # 验证魔数（前28字节）
        if header[:28] != self.MAGIC_HEADER:
            return False
        
        # 提取私钥（从0x1c到0x2c，16字节）
        self.own_key[:16] = header[0x1c:0x2c]
        # 第17字节为0
        self.own_key[16] = 0
        
        return True
    
    def _get_pub_key_data(self):
        """获取公钥数据（从十六进制字符串解码并解压）"""
        if self._pub_key_data is None:
            # 检查是否已提供十六进制字符串
            if not KUGOU_KEY_XZ_HEX:
                raise ValueError("请先在代码中粘贴密钥数据")
            
            print("正在加载解密密钥...")
            try:
                # 从十六进制字符串解码
                xz_data = bytes.fromhex(KUGOU_KEY_XZ_HEX)
                print(f"✓ 密钥数据大小: {len(xz_data):,} 字节")
                
                # 在内存中解压
                xz_file = io.BytesIO(xz_data)
                with lzma.open(xz_file, 'rb') as f:
                    self._pub_key_data = f.read()
                print(f"✓ 密钥解压完成，大小: {len(self._pub_key_data):,} 字节")
                
            except Exception as e:
                raise ValueError(f"密钥处理失败: {e}")
        
        return self._pub_key_data
    
    def _get_pub_key_for_range(self, start_idx, end_idx):
        """获取公钥片段"""
        # 获取公钥数据
        pub_key_data = self._get_pub_key_data()
        
        # 计算在公钥数据中的位置
        pub_key_start = start_idx // self.PUB_KEY_LEN_MAGNIFICATION
        pub_key_end = (end_idx // self.PUB_KEY_LEN_MAGNIFICATION) + 1
        
        # 确保索引在范围内
        if pub_key_start >= len(pub_key_data):
            return b''
        
        pub_key_end = min(pub_key_end, len(pub_key_data))
        
        if pub_key_start >= pub_key_end:
            return b''
        
        return pub_key_data[pub_key_start:pub_key_end]
    
    def read(self, size=65536):
        """读取并解密数据"""
        # 读取加密数据
        encrypted_data = self.input_file.read(size)
        if not encrypted_data:
            return b''
        
        # 获取对应的公钥片段
        pub_key_fragment = self._get_pub_key_for_range(self.pos, self.pos + len(encrypted_data))
        
        # 解密数据
        decrypted_data = bytearray(len(encrypted_data))
        
        # 预计算常量，提高性能
        own_key_len = self.OWN_KEY_LEN
        magnification = self.PUB_KEY_LEN_MAGNIFICATION
        mend_len = len(self.PUB_KEY_MEND)
        
        # 计算起始的公钥索引
        start_pub_key_index = self.pos // magnification
        
        for i in range(len(encrypted_data)):
            # 当前绝对位置（从加密数据开始处计算）
            current_abs_pos = self.pos + i
            
            # 获取加密字节
            encrypted_byte = encrypted_data[i]
            
            # 1. 私钥处理
            own_key_val = self.own_key[current_abs_pos % own_key_len] ^ encrypted_byte
            own_key_val = own_key_val ^ ((own_key_val & 0x0F) << 4)
            
            # 2. 公钥处理
            # 计算公钥索引
            pub_key_index = current_abs_pos // magnification
            
            # 在片段中的索引
            fragment_index = pub_key_index - start_pub_key_index
            
            # 获取公钥字节
            if 0 <= fragment_index < len(pub_key_fragment):
                pub_key_byte = pub_key_fragment[fragment_index]
            else:
                pub_key_byte = 0
            
            # 应用修正表
            mend_index = current_abs_pos % mend_len
            pub_key_val = self.PUB_KEY_MEND[mend_index] ^ pub_key_byte
            
            pub_key_val = pub_key_val ^ ((pub_key_val & 0x0F) << 4)
            
            # 3. 结合结果
            decrypted_data[i] = own_key_val ^ pub_key_val
        
        # 更新位置
        self.pos += len(encrypted_data)
        
        return bytes(decrypted_data)
    
    def read_all(self):
        """读取并解密所有数据"""
        result = bytearray()
        
        while True:
            chunk = self.read(65536)
            if not chunk:
                break
            result.extend(chunk)
        
        return bytes(result)

def detect_audio_format(data):
    """检测音频格式 - 简化版"""
    if len(data) < 4:
        return "dat"
    
    # MP3检测
    if data[:3] == b'ID3':
        return "mp3"
    
    # 检查MPEG帧头
    if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0:
        return "mp3"
    
    # FLAC检测
    if data[:4] == b'fLaC':
        return "flac"
    
    # WAV检测
    if len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WAVE':
        return "wav"
    
    # OGG检测
    if data[:4] == b'OggS':
        return "ogg"
    
    # M4A/MP4检测
    if len(data) >= 12:
        # 查找ftyp
        for i in range(min(len(data)-8, 32)):  # 通常在文件开头
            if data[i:i+4] == b'ftyp':
                if i+8 < len(data):
                    brand = data[i+4:i+8]
                    if brand in [b'M4A ', b'MP4A', b'mp42', b'isom']:
                        return "m4a"
                break
    
    return "dat"

def decrypt_file(input_path, output_path=None):
    """解密单个文件"""
    try:
        # 检查密钥数据
        if not KUGOU_KEY_XZ_HEX:
            print("错误: 未找到密钥数据")
            print("")
            print("请按以下步骤操作：")
            print("1. 运行配套的密钥提取工具\"转二进制.py\"将\"kugou_key.xz\"生成为\"kugou_key_simple.py\"")
            print("2. 复制生成\"kugou_key_simple.py\"文件中的KUGOU_KEY_XZ_HEX值")
            print("3. 打开本文件，在第15行粘贴该值")
            print("4. 保存文件后重新运行本文件，即可生效解密功能")
            return False
        
        input_path_obj = Path(input_path)
        
        if not input_path_obj.exists():
            print(f"错误：文件不存在 {input_path}")
            return False
        
        file_size = input_path_obj.stat().st_size
        print(f"正在处理: {input_path_obj.name}")
        print(f"文件大小: {file_size:,} 字节")
        
        # 打开文件并解密
        with open(input_path_obj, 'rb') as f:
            try:
                decoder = KuGouDecoder(f)
                
                print("开始解密文件...")
                
                # 解密整个文件
                decrypted_data = bytearray()
                chunk_size = 64 * 1024
                total_decrypted = 0
                total_to_decrypt = max(0, file_size - 1024)  # 减去1024字节的文件头
                
                if total_to_decrypt <= 0:
                    print("错误：文件太小或无效")
                    return False
                
                while True:
                    chunk = decoder.read(chunk_size)
                    if not chunk:
                        break
                    
                    decrypted_data.extend(chunk)
                    total_decrypted += len(chunk)
                    
                    # 显示进度
                    if total_to_decrypt > 0:
                        progress = (total_decrypted / total_to_decrypt) * 100
                        print(f"\r解密进度: {progress:.1f}%", end='')
                
                print(f"\n✓ 解密完成，共处理 {total_decrypted:,} 字节")
                
                if total_decrypted == 0:
                    print("错误：解密后无数据")
                    return False
                
                # 检测格式
                audio_format = detect_audio_format(decrypted_data[:4096])
                print(f"检测到音频格式: {audio_format.upper()}")
                
                # 确定输出路径
                if output_path is None:
                    # 移除.kgm或.kgm.flac扩展名
                    stem = input_path_obj.stem
                    if stem.lower().endswith('.kgm'):
                        stem = stem[:-4]
                    
                    output_path_obj = input_path_obj.with_name(f"{stem}.{audio_format}")
                    
                    # 避免覆盖
                    counter = 1
                    while output_path_obj.exists():
                        output_path_obj = input_path_obj.with_name(
                            f"{stem}_{counter}.{audio_format}"
                        )
                        counter += 1
                else:
                    output_path_obj = Path(output_path)
                    if output_path_obj.suffix.lower() != f".{audio_format}":
                        output_path_obj = output_path_obj.with_suffix(f".{audio_format}")
                
                # 写入文件
                print(f"保存文件到: {output_path_obj}")
                with open(output_path_obj, 'wb') as out_f:
                    out_f.write(decrypted_data)
                
                output_size = output_path_obj.stat().st_size
                print(f"✓ 保存完成，文件大小: {output_size:,} 字节")
                print("=" * 50)
                
                return True
                
            except ValueError as e:
                print(f"解密错误: {e}")
                return False
                
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("酷狗音乐解密工具")
    print("=" * 60)
    
    # 检查密钥数据
    if not KUGOU_KEY_XZ_HEX:
        print("错误: 未找到密钥数据")
        print("=" * 60)
        print("请按以下步骤操作：")
        print("1. 运行配套的密钥提取工具\"转二进制.py\"将\"kugou_key.xz\"生成为\"kugou_key_simple.py\"")
        print("2. 复制生成\"kugou_key_simple.py\"文件中的KUGOU_KEY_XZ_HEX值")
        print("3. 打开本文件，在第15行粘贴该值")
        print("4. 保存文件后重新运行本文件，即可生效解密功能")
        print("")
        input("按回车键退出...")
        return
    
    # 获取命令行参数
    if len(sys.argv) < 2:
        print("使用方法：")
        print("1. 将加密的kgm或kgm.flac文件拖放到此脚本上")
        print("2. 或使用命令行: python script.py 文件1.kgm 文件2.kgm.flac")
        print("3. 可以同时选中拖动多个文件文件夹进行解密处理")
        print("")
        input("按回车键退出...")
        return
    
    # 处理每个文件
    successful = 0
    total = len(sys.argv) - 1
    
    print(f"发现 {total} 个文件待处理")
    print("=" * 60)
    
    for i, file_path in enumerate(sys.argv[1:], 1):
        print(f"处理文件 {i}/{total}:")
        if decrypt_file(file_path):
            successful += 1
    
    print("处理完成")
    print(f"成功: {successful} 个文件，失败: {total - successful} 个文件")
    print("")
    
    if successful > 0:
        print("✓ 解密完成！您可以在原文件同目录下找到转换后的音频文件")
    
    input("按回车键退出...")

if __name__ == "__main__":
    main()