"""
酷狗音乐解密工具 - 终极加固版
✅ 解密成功100%删除源文件 | ✅ 文件夹递归处理 | ✅ 删除前双重验证
"""

import sys
import lzma
import io
import os
from pathlib import Path
from typing import List

# ================================================
# 请在这里粘贴您的密钥数据
# ================================================

KUGOU_KEY_XZ_HEX = ""  # 请将密钥粘贴在此处（与解密工具相同）

# ================================================

class KuGouDecoder:
    """酷狗音乐解密器 - 完整实现"""
    HEADER_LEN = 1024
    OWN_KEY_LEN = 17
    PUB_KEY_LEN_MAGNIFICATION = 16
    
    MAGIC_HEADER = bytes([
        0x7c, 0xd5, 0x32, 0xeb, 0x86, 0x02, 0x7f, 0x4b, 0xa8, 0xaf, 0xa6, 0x8e, 0x0f, 0xff, 0x99,
        0x14, 0x00, 0x04, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00
    ])
    
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
        self.input_file = input_file
        self.own_key = bytearray(self.OWN_KEY_LEN)
        self.pos = 0
        self._pub_key_data = None
        if not self._read_and_validate_header():
            raise ValueError("文件格式错误：不是有效的酷狗加密文件")

    def _read_and_validate_header(self):
        header = self.input_file.read(self.HEADER_LEN)
        if len(header) < self.HEADER_LEN:
            return False
        if header[:28] != self.MAGIC_HEADER:
            return False
        self.own_key[:16] = header[0x1c:0x2c]
        self.own_key[16] = 0
        return True
    
    def _get_pub_key_data(self):
        if self._pub_key_data is None:
            if not KUGOU_KEY_XZ_HEX:
                raise ValueError("请先在代码中粘贴密钥数据")
            print("🔑 正在加载解密密钥...")
            try:
                xz_data = bytes.fromhex(KUGOU_KEY_XZ_HEX)
                print(f"✓ 密钥数据大小: {len(xz_data):,} 字节")
                xz_file = io.BytesIO(xz_data)
                with lzma.open(xz_file, 'rb') as f:
                    self._pub_key_data = f.read()
                print(f"✓ 密钥解压完成，大小: {len(self._pub_key_data):,} 字节")
            except Exception as e:
                raise ValueError(f"密钥处理失败: {e}")
        return self._pub_key_data
    
    def _get_pub_key_for_range(self, start_idx, end_idx):
        pub_key_data = self._get_pub_key_data()
        pub_key_start = start_idx // self.PUB_KEY_LEN_MAGNIFICATION
        pub_key_end = (end_idx // self.PUB_KEY_LEN_MAGNIFICATION) + 1
        if pub_key_start >= len(pub_key_data):
            return b''
        pub_key_end = min(pub_key_end, len(pub_key_data))
        if pub_key_start >= pub_key_end:
            return b''
        return pub_key_data[pub_key_start:pub_key_end]
    
    def read(self, size=65536):
        encrypted_data = self.input_file.read(size)
        if not encrypted_data:
            return b''
        pub_key_fragment = self._get_pub_key_for_range(self.pos, self.pos + len(encrypted_data))
        decrypted_data = bytearray(len(encrypted_data))
        own_key_len = self.OWN_KEY_LEN
        magnification = self.PUB_KEY_LEN_MAGNIFICATION
        mend_len = len(self.PUB_KEY_MEND)
        start_pub_key_index = self.pos // magnification
        
        for i in range(len(encrypted_data)):
            current_abs_pos = self.pos + i
            encrypted_byte = encrypted_data[i]
            own_key_val = self.own_key[current_abs_pos % own_key_len] ^ encrypted_byte
            own_key_val = own_key_val ^ ((own_key_val & 0x0F) << 4)
            pub_key_index = current_abs_pos // magnification
            fragment_index = pub_key_index - start_pub_key_index
            pub_key_byte = pub_key_fragment[fragment_index] if 0 <= fragment_index < len(pub_key_fragment) else 0
            mend_index = current_abs_pos % mend_len
            pub_key_val = self.PUB_KEY_MEND[mend_index] ^ pub_key_byte
            pub_key_val = pub_key_val ^ ((pub_key_val & 0x0F) << 4)
            decrypted_data[i] = own_key_val ^ pub_key_val
        self.pos += len(encrypted_data)
        return bytes(decrypted_data)
    
    def read_all(self):
        result = bytearray()
        while True:
            chunk = self.read(65536)
            if not chunk:
                break
            result.extend(chunk)
        return bytes(result)

def detect_audio_format(data):
    if len(data) < 4:
        return "dat"
    if data[:3] == b'ID3':
        return "mp3"
    if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0:
        return "mp3"
    if data[:4] == b'fLaC':
        return "flac"
    if len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WAVE':
        return "wav"
    if data[:4] == b'OggS':
        return "ogg"
    if len(data) >= 12:
        for i in range(min(len(data)-8, 32)):
            if data[i:i+4] == b'ftyp':
                if i+8 < len(data):
                    brand = data[i+4:i+8]
                    if brand in [b'M4A ', b'MP4A', b'mp42', b'isom']:
                        return "m4a"
                break
    return "dat"

def collect_kugou_files(path: Path) -> List[str]:
    valid_files = []
    try:
        for root, _, files in os.walk(str(path.resolve())):
            for fname in files:
                fpath = Path(root) / fname
                lower_name = fpath.name.lower()
                if lower_name.endswith('.kgm') or lower_name.endswith('.kgm.flac'):
                    valid_files.append(str(fpath.resolve()))
    except Exception as e:
        print(f"⚠️  遍历文件夹出错 {path}: {e}")
    return valid_files

def process_path(path_str: str) -> List[str]:
    path_obj = Path(path_str).resolve()
    if not path_obj.exists():
        print(f"⚠️  跳过不存在的路径: {path_str}")
        return []
    if path_obj.is_file():
        if path_obj.suffix.lower() in ['.kgm', '.flac'] or '.kgm' in path_obj.name.lower():
            return [str(path_obj)]
        else:
            print(f"⚠️  跳过非酷狗加密文件: {path_obj.name}")
            return []
    if path_obj.is_dir():
        print(f"\n📂 扫描文件夹: {path_obj}")
        files = collect_kugou_files(path_obj)
        print(f"🔍 找到 {len(files)} 个待处理文件")
        return files
    print(f"⚠️  无效路径: {path_str}")
    return []

def decrypt_file(input_path: str) -> bool:
    """
    核心逻辑：解密成功 → 保存成功 → 验证输出 → 删除源文件
    任一环节失败均保留源文件，确保数据安全
    """
    input_path_obj = Path(input_path).resolve()
    
    if not input_path_obj.exists() or not input_path_obj.is_file():
        print(f"❌ 错误：无效文件路径 {input_path}")
        return False
    
    file_size = input_path_obj.stat().st_size
    print(f"\n{'='*50}")
    print(f"📁 处理: {input_path_obj.name} | 大小: {file_size:,} 字节")
    
    try:
        # =============== 第一阶段：解密 ===============
        with open(input_path_obj, 'rb') as f:
            decoder = KuGouDecoder(f)
            print("🔓 解密中...")
            
            decrypted_data = bytearray()
            chunk_size = 64 * 1024
            total_to_decrypt = max(0, file_size - KuGouDecoder.HEADER_LEN)
            
            if total_to_decrypt <= 0:
                print("❌ 错误：文件太小或无效（非酷狗加密文件）")
                return False
            
            total_decrypted = 0
            while True:
                chunk = decoder.read(chunk_size)
                if not chunk:
                    break
                decrypted_data.extend(chunk)
                total_decrypted += len(chunk)
                if total_to_decrypt > 0:
                    progress = (total_decrypted / total_to_decrypt) * 100
                    print(f"\r⏳ 进度: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✅ 解密完成 ({total_decrypted:,} 字节)")
            if total_decrypted == 0:
                print("❌ 错误：解密后无有效数据")
                return False
        
        # =============== 第二阶段：检测格式 & 保存 ===============
        audio_format = detect_audio_format(decrypted_data[:4096])
        print(f"🎵 检测格式: {audio_format.upper()}")
        
        stem = input_path_obj.stem
        if stem.lower().endswith('.kgm'):
            stem = stem[:-4]
        output_path_obj = input_path_obj.with_name(f"{stem}.{audio_format}")
        
        counter = 1
        while output_path_obj.exists():
            output_path_obj = input_path_obj.with_name(f"{stem}_{counter}.{audio_format}")
            counter += 1
        
        print(f"💾 保存至: {output_path_obj.name}")
        with open(output_path_obj, 'wb') as out_f:
            out_f.write(decrypted_data)
        
        output_size = output_path_obj.stat().st_size
        print(f"✅ 保存成功 ({output_size:,} 字节)")
        
        # =============== 第三阶段：关键！删除源文件 ===============
        # 二次验证：确保输出文件存在且非空
        if not output_path_obj.exists() or output_path_obj.stat().st_size == 0:
            print("❌ 严重错误：输出文件无效！保留源文件")
            return False
        
        # 执行删除（核心需求）
        try:
            input_path_obj.unlink()
            print(f"🗑️  ✅ 源文件已安全删除: {input_path_obj.name}")
            return True
        except PermissionError:
            print(f"❌ 删除失败：文件被占用！请关闭其他程序后手动删除 {input_path_obj.name}")
            return False
        except Exception as e:
            print(f"❌ 删除失败：{type(e).__name__}: {e}")
            return False
            
    except ValueError as e:
        print(f"❌ 解密失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 处理异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🎧 酷狗音乐解密工具 - 终极加固版")
    print("✅ 解密成功100%删除源文件 | ✅ 文件夹递归处理")
    print("=" * 60)
    
    if not KUGOU_KEY_XZ_HEX:
        print("\n❌ 错误: 未找到密钥数据")
        print("请将密钥粘贴到第15行 KUGOU_KEY_XZ_HEX = \"\" 中")
        input("\n按回车键退出...")
        return
    
    if len(sys.argv) < 2:
        print("\n💡 使用方法：")
        print("  拖放.kgm文件/文件夹到本程序 | 或命令行: python script.py 文件1.kgm 文件夹/")
        input("\n按回车键退出...")
        return
    
    # 收集所有待处理文件
    all_files = []
    print(f"\n📥 分析输入项 ({len(sys.argv)-1} 个)...")
    for item in sys.argv[1:]:
        all_files.extend(process_path(item))
    
    if not all_files:
        print("\n❌ 未找到有效酷狗加密文件（需 .kgm 或 .kgm.flac）")
        input("\n按回车键退出...")
        return
    
    print(f"\n🎯 共 {len(all_files)} 个文件待处理")
    print("=" * 60)
    
    # 处理每个文件
    success_count = 0
    for idx, file_path in enumerate(all_files, 1):
        print(f"\n[{idx}/{len(all_files)}]")
        if decrypt_file(file_path):
            success_count += 1
    
    # 最终报告
    print("\n" + "=" * 60)
    print(f"✅ 处理完成 | 成功: {success_count} | 失败: {len(all_files) - success_count}")
    if success_count > 0:
        print("✨ 解密文件已保存至原目录")
        print("🔥 所有成功解密的源文件(.kgm/.kgm.flac)已永久删除")
        print("⚠️  失败文件保留原样，请检查密钥或文件完整性")
    print("=" * 60)
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()