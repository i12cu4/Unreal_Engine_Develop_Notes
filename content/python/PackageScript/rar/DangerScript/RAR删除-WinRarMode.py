"""
RAR压缩包智能清理工具（无报告精简快速版）
核心特性：
✅ 智能路径过滤（根治错误码10）｜✅ 无报告零负担｜✅ 极致速度（直接删除）
✅ 路径存在性验证｜✅ 实时进度反馈｜✅ 中文路径基础支持
适用场景：个人素材批量清理｜扁平结构压缩包｜追求速度优先场景
"""
import os
import subprocess
from tqdm import tqdm

# ===================== 用户配置区域 =====================
RAR_EXE = r"C:\Program File\WinRAR\rar.exe"
TARGET_DIR = r"E:\Games\UE4_Assets"
delete_patterns = ["Saved", "Intermediate", "Build", "Binaries", ".vs", ".svn", "DerivedDataCache","使用教程【必看】",
                   "Read me.rar", "更多免费软件素材1.jpg",
                   "首页-虚幻4资源站-淘宝网.url", "2d素材库-传奇素材包-素材免费下载.url", "2d素材库素材免费下载.url", "3d模型-爱给模型库-素材免费下载.url","3d模型素材免费下载.url","51render.url",
                   "虚幻(UE)素材免费下载.url", "源码素材免费下载.url","CG3DA - 免费下载各类精品CG资源 .url",
                   "爱给网-2d素材库-免费下载.txt", "爱给网-虚幻(UE)-免费下载.txt", "爱给网-源码-免费下载.txt","必看!UE4资源使用说明.txt","爱给网-3d模型-免费下载.txt","免责声明.txt",
                   "UE4资源安装说明.txt","免责声明【必看】.txt","  UE多个高质量写实风景地貌场景模型_-传奇素材包-素材说明.txt",
                   "UE4库文件使用教程.docx"]
SILENT_MODE = True  # 静默运行（不弹出命令行窗口）
BATCH_SIZE = 100    # 单次删除条目上限（防命令过长）
# ================================================================

def get_silent_args():
    """获取静默模式参数（Windows专属）"""
    if os.name == 'nt' and SILENT_MODE:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return {'startupinfo': si}
    return {}

def filter_parent_entries(entries):
    """智能过滤：仅保留顶层删除项（根治错误码10）"""
    normalized_map = {}
    for entry in entries:
        norm = entry.replace('\\', '/').strip('/')
        if norm:  # 跳过空路径
            normalized_map[norm] = entry
    
    filtered = []
    for norm_path, orig_path in normalized_map.items():
        parts = norm_path.split('/')
        # 检查是否存在父目录已在删除列表中
        has_parent = any('/'.join(parts[:i]) in normalized_map for i in range(1, len(parts)))
        if not has_parent:
            filtered.append(orig_path)
    return filtered

def get_entries_to_delete(rar_path):
    """扫描需删除的条目（含智能过滤）"""
    try:
        cmd = [RAR_EXE, 'lb', rar_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, **get_silent_args())
        raw_entries = result.stdout.splitlines()
        
        # 筛选匹配项
        candidates = []
        for entry in raw_entries:
            norm = entry.replace('\\', '/').strip('/')
            parts = [p for p in norm.split('/') if p]
            if any(p in DELETE_PATTERNS for p in parts):
                candidates.append(entry)
        
        # 智能去重（关键！）
        return filter_parent_entries(list(set(candidates)))
    except Exception as e:
        tqdm.write(f"[!] 扫描失败: {os.path.basename(rar_path)} | {str(e)[:50]}")
        return []

def process_rar(rar_path):
    """直接删除RAR内冗余项（无解压）"""
    entries = get_entries_to_delete(rar_path)
    if not entries:
        return 0, set()
    
    try:
        # 分批删除（防命令过长）
        for i in range(0, len(entries), BATCH_SIZE):
            batch = entries[i:i+BATCH_SIZE]
            cmd = [RAR_EXE, 'd', '-idq', rar_path] + batch
            subprocess.run(cmd, check=True, **get_silent_args())
        
        # 统计匹配模式（用于反馈）
        matched = set()
        for entry in entries:
            parts = entry.replace('\\', '/').split('/')
            matched.update(set(parts) & set(DELETE_PATTERNS))
        return len(entries), matched
    except subprocess.CalledProcessError as e:
        msg = str(e)
        if "Cannot find" in msg:
            msg += "（父目录已删，属正常现象）"
        raise Exception(msg)
    except Exception as e:
        raise Exception(str(e))

# ===================== 主程序（极致精简） =====================
if __name__ == "__main__":
    # 1. 收集RAR文件
    rar_files = []
    try:
        for root, _, files in os.walk(TARGET_DIR):
            rar_files.extend(os.path.join(root, f) for f in files if f.lower().endswith('.rar'))
        if not rar_files:
            print(f"❌ 未在 [{TARGET_DIR}] 找到RAR文件！请检查路径配置")
            exit(1)
        print(f"✅ 发现 {len(rar_files)} 个RAR文件，开始清理...\n")
    except Exception as e:
        print(f"❌ 目录扫描失败: {str(e)}")
        exit(1)
    
    # 2. 处理核心（无报告存储，实时反馈）
    success_count = fail_count = skip_count = total_deleted = 0
    
    with tqdm(rar_files, desc="🚀 清理进度", unit="文件", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
        for rar_path in pbar:
            filename = os.path.basename(rar_path)
            pbar.set_postfix(当前=filename[:18])
            
            try:
                # 路径有效性验证
                if not os.path.isfile(rar_path):
                    raise FileNotFoundError("文件不存在或被占用")
                
                deleted, patterns = process_rar(rar_path)
                
                if deleted > 0:
                    total_deleted += deleted
                    success_count += 1
                    status = f"✓ 删{deleted}项"
                    detail = f" | {' '.join(list(patterns)[:3])}" if patterns else ""
                    pbar.write(f"[{status}] {filename[:40]:<42}{detail}")
                else:
                    skip_count += 1
                    pbar.write(f"[○ 跳过] {filename}")
                    
            except Exception as e:
                fail_count += 1
                err_msg = str(e).replace('\n', ' ').replace('\r', '')[:60]
                pbar.write(f"[✗ 失败] {filename[:40]:<42}→ {err_msg}")
    
    # 3. 最终统计（仅1行摘要，无详细报告）
    print(f"\n{'='*60}")
    print(f"✅ 完成！成功:{success_count} | 跳过:{skip_count} | 失败:{fail_count} | 累计清理:{total_deleted}项")
    print(f"💡 提示：失败文件请检查路径/权限/压缩包完整性（错误码10已通过智能过滤规避）")
    print(f"{'='*60}")