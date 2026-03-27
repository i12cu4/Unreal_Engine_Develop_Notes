"""
RAR压缩包删除冗余文件工具 [增强版]
功能:
1. 智能识别需要删除的文件/目录
2. 安全替换机制防止数据丢失
3. 支持控制台/CSV双报告模式
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

# 报告数据结构
class ProcessResult:
    def __init__(self, rar_path):
        self.rar_path = rar_path
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

def should_process(rar_path):
    """检查压缩包是否需要处理"""
    try:
        cmd = [rar_exe_path, 'vb', rar_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, **get_silent_args())
        entries = result.stdout.splitlines()
        
        for entry in entries:
            entry = entry.strip().replace('\\', '/').rstrip('/')
            if any(part in delete_patterns for part in entry.split('/')):
                return True
        return False
    except Exception as e:
        print(f"压缩包扫描失败: {os.path.basename(rar_path)} - {str(e)}")
        return True

def safe_compress(temp_dir, original_rar):
    """安全压缩流程：生成临时文件，验证成功后替换原文件"""
    temp_rar = f"{original_rar}.temp"
    
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
    shutil.move(temp_rar, original_rar)

def process_rar(rar_path, result):
    """处理单个RAR文件"""
    if not should_process(rar_path):
        result.success = True
        return

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压
            extract_cmd = [winrar_exe_path, 'x', '-ibck', '-y', rar_path, temp_dir]
            subprocess.run(extract_cmd, check=True, **get_silent_args())

            # 删除操作
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                # 文件处理
                for file in files:
                    if file in delete_patterns:
                        full_path = os.path.join(root, file)
                        os.remove(full_path)
                        result.deleted_files.append(os.path.relpath(full_path, temp_dir))
                
                # 目录处理
                for dir_name in dirs:
                    if dir_name in delete_patterns:
                        full_path = os.path.join(root, dir_name)
                        shutil.rmtree(full_path)
                        result.deleted_dirs.append(os.path.relpath(full_path, temp_dir))

            # 安全压缩并替换
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
    """生成CSV报告"""
    csv_path = os.path.join(CSV_SAVE_DIR, f"RAR清理报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    with open(csv_path, 'w', newline='', encoding='gbk') as f:
        writer = csv.writer(f)
        writer.writerow(["压缩包路径", "状态", "删除文件", "删除目录", "错误信息"])
        
        for res in results:
            status = "成功" if res.success else "失败"
            files = ";".join(res.deleted_files) if res.deleted_files else ""
            dirs = ";".join(res.deleted_dirs) if res.deleted_dirs else ""
            writer.writerow([res.rar_path, status, files, dirs, res.error_msg or ""])
    
    return csv_path

if __name__ == "__main__":
    # 收集RAR文件
    rar_files = []
    for root, _, files in os.walk(target_dir):
        rar_files.extend(os.path.join(root, f) for f in files if f.lower().endswith('.rar'))

    # 处理文件并收集结果
    results = []
    with tqdm(rar_files, desc="处理进度", unit="个") as pbar:
        for rar in pbar:
            pbar.set_postfix(file=os.path.basename(rar)[:15])
            result = ProcessResult(rar)
            try:
                process_rar(rar, result)
            except Exception as e:
                result.error_msg = str(e)
                result.success = False
            results.append(result)

    # 生成报告
    if REPORT_TYPE in ("console", "both"):
        generate_console_report(results)
    
    csv_path = None
    if REPORT_TYPE in ("csv", "both"):
        csv_path = generate_csv_report(results)
    
    if csv_path:
        print(f"\n{'='*50}\nCSV报告路径: {csv_path}")