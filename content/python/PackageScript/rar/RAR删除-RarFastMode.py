"""
RAR压缩包删除冗余文件工具（高效版）增强报告版
功能:
1. 直接删除RAR压缩包中的指定文件和文件夹，无需解压/重新压缩
2. 支持控制台、CSV或双重报告输出
3. 实时显示处理进度和结果
4. 自动生成带时间戳的CSV报告
"""
import os
import csv
import subprocess
from datetime import datetime
from tqdm import tqdm
from collections import namedtuple

# ===================== 用户配置区域 =====================
rar_exe_path = r"C:\Program File\WinRAR\rar.exe"
target_dir = r"C:\Users\chru\Desktop\1"
delete_patterns = ["Saved", "Intermediate", "Build", "Binaries", ".vs", ".svn", "DerivedDataCache",
                   "Read me.rar", "更多免费软件素材1.jpg",
                   "首页-虚幻4资源站-淘宝网.url", "2d素材库-传奇素材包-素材免费下载.url", "2d素材库素材免费下载.url", 
                   "虚幻(UE)素材免费下载.url", "源码素材免费下载.url","CG3DA - 免费下载各类精品CG资源 .url",
                   "爱给网-2d素材库-免费下载.txt", "爱给网-虚幻(UE)-免费下载.txt", "爱给网-源码-免费下载.txt",
                   "UE4资源安装说明.txt","免责声明【必看】.txt","  UE多个高质量写实风景地貌场景模型_-传奇素材包-素材说明.txt"]
silent_mode = True  # 静默模式开关
REPORT_TYPE = "both"  # 报告类型: console/csv/both
# ======================================================

# 定义结果数据结构
ResultItem = namedtuple('ResultItem', ['rar_path', 'success', 'deleted_count', 'error_msg', 'patterns'])

def get_silent_args():
    """获取静默模式参数"""
    if os.name == 'nt' and silent_mode:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return {'startupinfo': si}
    return {}

def get_entries_to_delete(rar_path):
    """获取需要删除的条目列表"""
    try:
        cmd = [rar_exe_path, 'lb', rar_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, **get_silent_args())
    except subprocess.CalledProcessError as e:
        print(f"无法列出压缩包内容: {os.path.basename(rar_path)} - {str(e)}")
        return []
    
    entries = result.stdout.splitlines()
    entries_to_delete = []
    
    for entry in entries:
        normalized = entry.replace('\\', '/').strip('/')
        parts = [p for p in normalized.split('/') if p]
        if any(part in delete_patterns for part in parts):
            entries_to_delete.append(entry)
    
    return list(set(entries_to_delete))  # 去重

def process_rar(rar_path):
    """直接通过RAR命令删除条目"""
    entries = get_entries_to_delete(rar_path)
    if not entries:
        return 0, set()

    try:
        # 构建删除命令（限制每次最多删除100个条目防止参数过长）
        batch_size = 100
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i+batch_size]
            cmd = [rar_exe_path, 'd', '-idq', rar_path] + batch
            subprocess.run(cmd, check=True, **get_silent_args())

        # 统计匹配模式
        matched = set()
        for entry in entries:
            parts = entry.replace('\\', '/').split('/')
            matched.update(set(parts) & set(delete_patterns))
        
        return len(entries), matched  # 返回实际删除数量

    except subprocess.CalledProcessError as e:
        raise Exception(f"RAR命令执行失败: {str(e)}")

def generate_console_report(results):
    """生成控制台报告"""
    print("\n" + "="*50)
    print("处理结果汇总:")
    for res in results:
        status = "[失败]" if not res.success else "[跳过]" if not res.deleted_count else "[成功]"
        base_info = f"{status} {os.path.basename(res.rar_path)}"
        
        if not res.success:
            print(f"{base_info} - 错误: {res.error_msg}")
        elif res.deleted_count:
            print(f"{base_info.ljust(40)} 删除: {res.deleted_count}项 | 匹配模式: {', '.join(res.patterns)}")
        else:
            print(base_info)
    print("="*50)

def generate_csv_report(results):
    """生成CSV报告（增强大数据处理）"""
    csv_name = f"RAR清理报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_path = os.path.join(target_dir, csv_name)
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["压缩包名称", "完整路径", "处理状态", "删除数量", "匹配模式", "错误信息"])
        
        for res in results:
            status = "成功" if res.success else "失败"
            patterns = ', '.join(res.patterns) if res.patterns else ""
            error = res.error_msg.encode('utf-8', 'replace').decode('utf-8') if res.error_msg else ""
            
            writer.writerow([
                os.path.basename(res.rar_path),
                res.rar_path,
                status,
                res.deleted_count,
                patterns,
                error
            ])
    
    return csv_path

if __name__ == "__main__":
    # 收集所有RAR文件
    rar_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith('.rar'):
                rar_files.append(os.path.join(root, file))

    results = []
    print(f"发现待处理RAR文件: {len(rar_files)}个")

    # 处理进度显示
    with tqdm(rar_files, desc="处理压缩包", unit="file", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        for rar_path in pbar:
            pbar.set_postfix(file=os.path.basename(rar_path)[:15])
            try:
                # 实时处理并记录结果
                deleted_count, patterns = process_rar(rar_path)
                success = True
                error_msg = None
                
                if deleted_count > 0:
                    status_str = f"删除{deleted_count}项".ljust(12)
                    pbar.write(f"[✓] {os.path.basename(rar_path)[:30].ljust(32)} {status_str} 匹配模式: {', '.join(patterns)}")
                else:
                    pbar.write(f"[○] {os.path.basename(rar_path)} 无需处理")

            except Exception as e:
                success = False
                error_msg = str(e)
                deleted_count = 0
                patterns = set()
                pbar.write(f"[×] 处理失败: {os.path.basename(rar_path)} - {error_msg}")

            # 记录结果
            results.append(ResultItem(
                rar_path=rar_path,
                success=success,
                deleted_count=deleted_count,
                error_msg=error_msg,
                patterns=patterns
            ))

    # 生成报告
    if REPORT_TYPE in ("console", "both"):
        generate_console_report(results)
    
    csv_path = None
    if REPORT_TYPE in ("csv", "both"):
        csv_path = generate_csv_report(results)
    
    if csv_path:
        print(f"\n{'='*50}\nCSV报告路径: {os.path.abspath(csv_path)}\n{'='*50}")


"""
偶现错误可能性分析:
可能性排序（按概率从高到低）

1.程序逻辑缺陷（85%概率）
典型表现：
    文件处理看似成功但报错
    错误集中在特定文件特征（如长路径、特殊字符）
核心原因：
    命令行参数构造不符合WinRAR规范（如双引号嵌套）
    未正确处理Windows路径长度限制（超过260字符）
    静默模式掩盖真实错误信息（-idq参数导致错误信息丢失）
2.文件访问冲突（10%概率）
典型表现：
    间歇性失败（同一文件多次运行结果不同）
    错误代码随机变化（如10/12/15等）
核心原因：
    压缩包被其他进程占用（资源管理器预览、杀毒软件扫描）
    用户权限不足（未以管理员身份运行）
3.压缩包自身问题（3%概率）
典型表现：
    特定压缩包反复失败
    手动使用WinRAR操作也会报错
核心原因：
    文件头损坏（可通过rar r命令修复）
    加密/分卷压缩包的特殊处理需求
4.硬件问题（2%概率）
典型表现：
    伴随其他文件操作异常（复制/删除失败）
    系统日志显示磁盘错误（事件查看器ID 7/11）
核心原因：
    硬盘坏道（特别是目标目录所在分区）
    内存故障导致数据传输错误

"""