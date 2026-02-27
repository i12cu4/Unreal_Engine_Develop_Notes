"""
RAR压缩包删除冗余文件工具 [Unicode安全版]
修复重点：
1. 子进程编码处理
2. 文件路径安全处理
3. CSV报告编码兼容性
4. 修复GBK访问编解码器无法解码
"""
import os
import csv
import subprocess
import tempfile
import shutil
from datetime import datetime
from tqdm import tqdm

# ===================== 用户配置区域 =====================
winrar_exe_path = r"C:\Program File\WinRAR\WinRAR.exe"
rar_exe_path = r"C:\Program File\WinRAR\Rar.exe"
target_dir = r"G:\agw"
delete_patterns = ["Saved", "Intermediate", "Build", "Binaries", ".vs", ".svn", "DerivedDataCache",
                   "Read me.rar", "更多免费软件素材1.jpg",
                   "首页-虚幻4资源站-淘宝网.url", "2d素材库-传奇素材包-素材免费下载.url", "2d素材库素材免费下载.url", 
                   "虚幻(UE)素材免费下载.url", "源码素材免费下载.url","CG3DA - 免费下载各类精品CG资源 .url",
                   "爱给网-2d素材库-免费下载.txt", "爱给网-虚幻(UE)-免费下载.txt", "爱给网-源码-免费下载.txt",
                   "UE4资源安装说明.txt","免责声明【必看】.txt","  UE多个高质量写实风景地貌场景模型_-传奇素材包-素材说明.txt"]
silent_mode = True    # 静默模式开关
REPORT_TYPE = "both"  # 报告类型: console/csv/both
CSV_SAVE_DIR = target_dir  # CSV保存目录，默认当前路径
# ======================================================

class ProcessResult:
    def __init__(self, rar_path):
        self.rar_path = os.fsdecode(rar_path)  # 路径编码规范化
        self.deleted_files = []
        self.deleted_dirs = []
        self.success = False
        self.error_msg = None

def get_silent_args():
    """获取静默模式参数"""
    if os.name == 'nt' and silent_mode:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return {'startupinfo': si}
    return {}

def safe_decode(byte_str):
    """安全解码字节字符串"""
    try:
        return byte_str.decode('utf-8')
    except UnicodeDecodeError:
        return byte_str.decode('gbk', errors='replace')

def should_process(rar_path):
    """检查压缩包是否需要处理（增强编码处理）"""
    try:
        cmd = [rar_exe_path, 'vb', os.fsencode(rar_path)]  # 处理原始字节路径
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            **get_silent_args()
        )
        
        # 安全解码输出内容
        entries = safe_decode(result.stdout).splitlines()
        
        for entry in entries:
            entry = entry.strip().replace('\\', '/').rstrip('/')
            if any(part in delete_patterns for part in entry.split('/')):
                return True
        return False
    except subprocess.CalledProcessError as e:
        error_msg = f"命令执行失败: {safe_decode(e.stderr)}" if e.stderr else str(e)
        print(f"压缩包扫描失败: {os.path.basename(rar_path)} - {error_msg}")
        return True
    except Exception as e:
        print(f"扫描异常: {os.path.basename(rar_path)} - {str(e)}")
        return True

def safe_compress(temp_dir, original_rar):
    """安全压缩流程"""
    temp_rar = f"{original_rar}.temp"
    original_rar_bytes = os.fsencode(original_rar)  # 处理字节路径
    
    try:
        # 生成临时压缩包
        compress_cmd = [
            winrar_exe_path,
            'a', '-r', '-ep1', '-ibck',
            temp_rar,
            os.path.join(temp_dir, '*')
        ]
        subprocess.run(compress_cmd, check=True, **get_silent_args())
        
        # 验证临时文件
        if not os.path.exists(temp_rar) or os.path.getsize(temp_rar) == 0:
            raise RuntimeError("生成的临时压缩包无效")
        
        # 替换原文件
        os.replace(temp_rar, original_rar_bytes)
    finally:
        if os.path.exists(temp_rar):
            os.remove(temp_rar)

def process_rar(rar_path, result):
    """处理单个RAR文件（增强编码处理）"""
    try:
        if not should_process(rar_path):
            result.success = True
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压
            extract_cmd = [
                winrar_exe_path,
                'x', '-ibck', '-y',
                os.fsencode(rar_path),  # 字节路径
                os.fsencode(temp_dir)
            ]
            subprocess.run(extract_cmd, check=True, **get_silent_args())

            # 删除操作
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                root_decoded = os.fsdecode(root)  # 解码路径
                
                # 处理文件
                for file in files:
                    file_decoded = os.fsdecode(file)
                    if file_decoded in delete_patterns:
                        full_path = os.path.join(root_decoded, file_decoded)
                        os.remove(full_path)
                        rel_path = os.path.relpath(full_path, temp_dir)
                        result.deleted_files.append(rel_path)

                # 处理目录
                for dir_name in dirs:
                    dir_decoded = os.fsdecode(dir_name)
                    if dir_decoded in delete_patterns:
                        full_path = os.path.join(root_decoded, dir_decoded)
                        shutil.rmtree(full_path, ignore_errors=True)
                        rel_path = os.path.relpath(full_path, temp_dir)
                        result.deleted_dirs.append(rel_path)

            # 安全压缩
            safe_compress(temp_dir, rar_path)
            result.success = True

    except Exception as e:
        result.error_msg = str(e)
        result.success = False

def generate_console_report(results):
    """生成控制台报告"""
    print("\n处理结果汇总:")
    for res in results:
        if not res.success:
            print(f"[失败] {res.rar_path} - 错误: {res.error_msg}")
            continue
        
        if not res.deleted_files and not res.deleted_dirs:
            print(f"[跳过] {res.rar_path} - 无匹配项")
            continue
        
        print(f"[成功] {res.rar_path}")
        if res.deleted_files:
            print("  删除文件:")
            for f in res.deleted_files:
                print(f"    - {f}")
        if res.deleted_dirs:
            print("  删除目录:")
            for d in res.deleted_dirs:
                print(f"    - {d}")

def generate_csv_report(results):
    """生成CSV报告（增强编码兼容性）"""
    csv_name = f"RAR清理报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_path = os.path.join(CSV_SAVE_DIR, csv_name)
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["压缩包路径", "状态", "删除文件", "删除目录", "错误信息"])
        
        for res in results:
            status = "成功" if res.success else "失败"
            
            # 安全处理字符串
            def safe_str(s):
                return s.encode('utf-8', 'replace').decode('utf-8') if isinstance(s, str) else str(s)
            
            files = ";".join(res.deleted_files) if res.deleted_files else ""
            dirs = ";".join(res.deleted_dirs) if res.deleted_dirs else ""
            
            writer.writerow([
                safe_str(res.rar_path),
                status,
                safe_str(files),
                safe_str(dirs),
                safe_str(res.error_msg) if res.error_msg else ""
            ])
    
    return csv_path

def format_single_result(result):
    """格式化单个结果输出"""
    if not result.success:
        return f"[失败] {result.rar_path} - 错误: {result.error_msg}"
    
    if not result.deleted_files and not result.deleted_dirs:
        return f"[跳过] {result.rar_path}"
    
    output = [
        f"[成功] {result.rar_path}",
        *[f"  删除文件: {f}" for f in result.deleted_files],
        *[f"  删除目录: {d}" for d in result.deleted_dirs]
    ]
    return "\n".join(output)

# 修改主程序部分
if __name__ == "__main__":
    # 收集RAR文件
    rar_files = []
    for root, _, files in os.walk(target_dir):
        rar_files.extend(os.path.join(root, f) for f in files if f.lower().endswith('.rar'))

    # 处理文件并实时输出
    results = []
    with tqdm(rar_files, desc="处理进度", unit="个", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        for rar in pbar:
            rar_path = os.fsdecode(rar)
            pbar.set_postfix(file=os.path.basename(rar_path)[:15])
            result = ProcessResult(rar_path)
            
            try:
                process_rar(rar_path, result)
            except Exception as e:
                result.error_msg = str(e)
                result.success = False
            
            # 实时输出处理结果
            if REPORT_TYPE in ("console", "both"):
                output = format_single_result(result)
                pbar.write(output)  # 使用tqdm的write方法避免打乱进度条
            
            results.append(result)
    
    # 生成报告
    if REPORT_TYPE in ("console", "both"):
        generate_console_report(results)
    
    csv_path = None
    if REPORT_TYPE in ("csv", "both"):
        csv_path = generate_csv_report(results)
    
    if csv_path:
        print(f"\n{'='*50}\nCSV报告路径: {csv_path}")