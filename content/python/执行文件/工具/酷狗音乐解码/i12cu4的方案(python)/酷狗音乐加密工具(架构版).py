"""
酷狗音乐加密工具
"""

import sys
import lzma
import io
import os
from pathlib import Path

# ================================================
# 请在这里粘贴您的密钥数据（与解密工具相同）
# ================================================

KUGOU_KEY_XZ_HEX = ""  # 请将密钥粘贴在此处（与解密工具相同）

# ================================================

class KuGouEncoder:
    """酷狗音乐加密器 - 基于正确解密的逆向实现"""
    
    # 常量定义（与解密器完全一致）
    HEADER_LEN = 1024  # 酷狗文件头固定长度
    OWN_KEY_LEN = 17   # 私钥长度
    PUB_KEY_LEN_MAGNIFICATION = 16  # 公钥索引放大倍数
    
    # 酷狗文件魔数（28字节）- 与解密器完全一致
    MAGIC_HEADER = bytes([
        0x7c, 0xd5, 0x32, 0xeb, 0x86, 0x02, 0x7f, 0x4b, 0xa8, 0xaf, 0xa6, 0x8e, 0x0f, 0xff, 0x99,
        0x14, 0x00, 0x04, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00
    ])
    
    # 公钥修正表（272字节）- 与解密器完全一致
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
    
    def __init__(self, output_file, own_key=None):
        """初始化加密器
        Args:
            output_file: 输出文件对象
            own_key: 可选的私钥（16字节），如果不提供则使用固定私钥
        """
        self.output_file = output_file
        self.own_key = bytearray(self.OWN_KEY_LEN)
        self.pos = 0  # 当前写入位置（从加密数据开始计算）
        self._pub_key_data = None
        
        # 设置私钥
        if own_key is not None and len(own_key) >= 16:
            # 使用提供的私钥
            self.own_key[:16] = own_key[:16]
            print(f"使用自定义私钥: {self.own_key[:16].hex().upper()}")
        else:
            # 使用固定私钥（确保一致性）
            # 注意：实际酷狗文件可能使用随机私钥，这里为了测试使用固定值
            import random
            for i in range(16):
                self.own_key[i] = random.randint(0, 255)
            print(f"使用随机私钥: {self.own_key[:16].hex().upper()}")
        
        # 第17字节为0
        self.own_key[16] = 0
        
        # 写入文件头
        self._write_header()
    
    def _write_header(self):
        """写入酷狗文件头"""
        header = bytearray(self.HEADER_LEN)
        
        # 写入魔数
        header[:28] = self.MAGIC_HEADER
        
        # 写入私钥（0x1c到0x2c）
        header[0x1c:0x2c] = self.own_key[:16]
        
        # 其余部分填充0
        for i in range(0x2c, self.HEADER_LEN):
            header[i] = 0
        
        self.output_file.write(header)
    
    def _get_pub_key_data(self):
        """获取公钥数据（从十六进制字符串解码并解压）"""
        if self._pub_key_data is None:
            # 检查是否已提供十六进制字符串
            if not KUGOU_KEY_XZ_HEX:
                raise ValueError("请先在代码中粘贴密钥数据")
            
            print("正在加载加密密钥...")
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
        """获取公钥片段 - 与解密器完全一致"""
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
    
    def _encrypt_chunk(self, plain_data):
        """加密数据块 - 解密算法的精确逆向"""
        # 获取对应的公钥片段
        pub_key_fragment = self._get_pub_key_for_range(self.pos, self.pos + len(plain_data))
        
        # 加密数据
        encrypted_data = bytearray(len(plain_data))
        
        # 预计算常量，提高性能
        own_key_len = self.OWN_KEY_LEN
        magnification = self.PUB_KEY_LEN_MAGNIFICATION
        mend_len = len(self.PUB_KEY_MEND)
        
        # 计算起始的公钥索引
        start_pub_key_index = self.pos // magnification
        
        for i in range(len(plain_data)):
            # 当前绝对位置
            current_abs_pos = self.pos + i
            
            # 获取明文字节
            plain_byte = plain_data[i]
            
            # ================================================
            # 加密算法：解密算法的精确逆向
            # ================================================
            
            # 1. 计算公钥部分（与解密算法相同）
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
            
            # 2. 计算own_key_val（与解密算法相同）
            own_key_val = plain_byte ^ pub_key_val
            
            # 3. 逆向计算 own_key_raw
            own_key_raw = own_key_val ^ ((own_key_val & 0x0F) << 4)
            
            # 4. 计算加密字节
            encrypted_byte = self.own_key[current_abs_pos % own_key_len] ^ own_key_raw
            
            encrypted_data[i] = encrypted_byte
        
        # 更新位置
        self.pos += len(plain_data)
        
        return bytes(encrypted_data)
    
    def encrypt(self, plain_data, chunk_size=65536):
        """加密数据（支持流式处理）"""
        total_encrypted = 0
        
        # 分块加密
        for i in range(0, len(plain_data), chunk_size):
            chunk = plain_data[i:i + chunk_size]
            encrypted_chunk = self._encrypt_chunk(chunk)
            self.output_file.write(encrypted_chunk)
            total_encrypted += len(encrypted_chunk)
            
            # 显示进度
            progress = (i + len(chunk)) / len(plain_data) * 100
            print(f"\r加密进度: {progress:.1f}%", end='')
        
        print()  # 换行
        return total_encrypted

def encrypt_file(input_path, output_path=None, custom_own_key=None):
    """加密单个文件为酷狗格式"""
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
        
        # 读取原始音频文件
        print("读取原始文件...")
        with open(input_path_obj, 'rb') as f:
            plain_data = f.read()
        
        # 确定输出路径
        if output_path is None:
            # 默认输出到同目录，扩展名为.kgm
            output_path_obj = input_path_obj.with_suffix('.kgm')
            
            # 避免覆盖
            counter = 1
            while output_path_obj.exists():
                output_path_obj = input_path_obj.with_name(
                    f"{input_path_obj.stem}_{counter}.kgm"
                )
                counter += 1
        else:
            output_path_obj = Path(output_path)
            if not output_path_obj.suffix.lower().endswith('.kgm'):
                output_path_obj = output_path_obj.with_suffix('.kgm')
        
        # 创建加密文件
        print(f"创建加密文件: {output_path_obj}")
        with open(output_path_obj, 'wb') as out_f:
            # 创建加密器
            encoder = KuGouEncoder(out_f, custom_own_key)
            
            print("开始加密文件...")
            
            # 加密数据
            total_encrypted = encoder.encrypt(plain_data)
            
            print(f"✓ 加密完成，共处理 {total_encrypted:,} 字节")
        
        output_size = output_path_obj.stat().st_size
        print(f"✓ 加密文件保存完成，文件大小: {output_size:,} 字节")
        print(f"  文件头: {encoder.HEADER_LEN} 字节")
        print(f"  加密数据: {total_encrypted:,} 字节")
        
        # 验证加密（可选）
        print("=" * 50)
        print("提示：您可以使用配套的解密工具验证加密文件")
        
        return True
        
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_encryption(original_file, encrypted_file):
    """验证加密正确性（使用解密工具）"""
    print("\n正在验证加密文件...")
    
    # 导入解密工具（假设在同一目录）
    try:
        # 临时方案：直接调用系统命令解密
        import subprocess
        import tempfile
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp_path = tmp.name
        
        # 调用解密工具
        decrypt_script = Path(__file__).with_name('kugou_decrypt.py')  # 假设解密脚本名为kugou_decrypt.py
        if not decrypt_script.exists():
            print("警告：未找到解密工具，无法验证")
            return False
        
        # 执行解密
        result = subprocess.run(
            [sys.executable, str(decrypt_script), str(encrypted_file), '-o', tmp_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"解密失败: {result.stderr}")
            return False
        
        # 比较文件
        with open(original_file, 'rb') as f1, open(tmp_path, 'rb') as f2:
            original_data = f1.read()
            decrypted_data = f2.read()
        
        if original_data == decrypted_data:
            print("✓ 加密验证通过：解密后的文件与原始文件完全相同")
            os.unlink(tmp_path)
            return True
        else:
            print("✗ 加密验证失败：解密后的文件与原始文件不同")
            # 找出第一个不同的字节
            for i, (b1, b2) in enumerate(zip(original_data, decrypted_data)):
                if b1 != b2:
                    print(f"第一个差异在位置 {i:08X}: 原始={b1:02X} 解密={b2:02X}")
                    break
            os.unlink(tmp_path)
            return False
            
    except Exception as e:
        print(f"验证过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("酷狗音乐加密工具")
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
        print("1. 将需要加密的文件拖放到此脚本上")
        print("2. 或使用命令行: python script.py 文件1.kgm 文件2.kgm.flac")
        print("3. 可以同时选中拖动多个文件文件夹进行解密处理")
        print("")
        print("可选参数：")
        print("  --verify    加密后验证文件正确性")
        print("  --key HEX   使用指定的16字节私钥（32字符十六进制）")
        print("")
        input("按回车键退出...")
        return
    
    # 解析参数
    verify = False
    custom_key = None
    files = []
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--verify":
            verify = True
            i += 1
        elif arg == "--key" and i + 1 < len(sys.argv):
            try:
                key_hex = sys.argv[i + 1]
                if len(key_hex) != 32:
                    print(f"错误：私钥长度必须为32个十六进制字符（16字节）")
                    return
                custom_key = bytes.fromhex(key_hex)
                i += 2
            except Exception as e:
                print(f"错误：无效的私钥格式: {e}")
                return
        elif arg.startswith("-"):
            print(f"警告：忽略未知参数 {arg}")
            i += 1
        else:
            files.append(arg)
            i += 1
    
    if not files:
        print("错误：未指定输入文件")
        return
    
    # 处理每个文件
    successful = 0
    total = len(files)
    
    print(f"发现 {total} 个文件待处理")
    if custom_key:
        print(f"使用自定义私钥: {custom_key.hex().upper()}")
    if verify:
        print("验证模式: 启用")
    print("=" * 60)
    
    for i, file_path in enumerate(files, 1):
        print(f"处理文件 {i}/{total}:")
        
        # 加密文件
        if encrypt_file(file_path, custom_own_key=custom_key):
            successful += 1
            
            # 如果需要验证
            if verify:
                # 假设加密文件在同一目录，扩展名为.kgm
                input_path = Path(file_path)
                encrypted_path = input_path.with_suffix('.kgm')
                
                # 检查是否生成了加密文件
                if encrypted_path.exists():
                    if verify_encryption(file_path, encrypted_path):
                        print("✓ 验证通过")
                    else:
                        print("✗ 验证失败")
                        successful -= 1  # 验证失败不算成功
                else:
                    print("警告：未找到生成的加密文件")
    
    print("处理完成")
    print(f"成功: {successful} 个文件，失败: {total - successful} 个文件")
    print("")
    
    if successful > 0:
        print("✓ 加密完成！已生成酷狗加密格式文件")
        print("  可以使用配套的解密工具验证加密文件")
    
    input("按回车键退出...")

if __name__ == "__main__":
    main()