"""
RAR压缩包删除冗余文件工具（高效版）增强报告版
功能:
1. 直接删除RAR压缩包中的指定文件和文件夹，无需解压/重新压缩
2. 支持控制台、CSV或双重报告输出
3. 实时显示处理进度和结果
4. 自动生成带时间戳的CSV报告
5. (可能)修复了错误码10的问题
"""
import os
import sys
import argparse
from pathlib import Path
import csv
import subprocess
from datetime import datetime
from tqdm import tqdm
from collections import namedtuple

# ===================== 用户配置区域 =====================
rar_exe_path = r"C:\Program Files\WinRAR\rar.exe"
delete_patterns = ["Saved", "Intermediate", "Build", "Binaries", ".vs", ".svn", "DerivedDataCache","使用教程【必看】",
                   "Read me.rar", "更多免费软件素材1.jpg",
                   "首页-虚幻4资源站-淘宝网.url", "2d素材库-传奇素材包-素材免费下载.url", "2d素材库素材免费下载.url", "3d模型-爱给模型库-素材免费下载.url","3d模型素材免费下载.url","51render.url",
                   "虚幻(UE)素材免费下载.url", "源码素材免费下载.url","CG3DA - 免费下载各类精品CG资源 .url",
                   "爱给网-2d素材库-免费下载.txt", "爱给网-虚幻(UE)-免费下载.txt", "爱给网-源码-免费下载.txt","必看!UE4资源使用说明.txt","爱给网-3d模型-免费下载.txt","免责声明.txt",
                   "UE4资源安装说明.txt","免责声明【必看】.txt","  UE多个高质量写实风景地貌场景模型_-传奇素材包-素材说明.txt",
                   "UE4库文件使用教程.docx"]
silent_mode = True  # 静默模式开关
REPORT_TYPE = "both"  # 报告类型: console/csv/both
# ======================================================

ResultItem = namedtuple('ResultItem', ['rar_path', 'success', 'deleted_count', 'error_msg', 'patterns'])

def get_silent_args():
    """获取静默模式参数"""
    if os.name == 'nt' and silent_mode:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return {'startupinfo': si}
    return {}

def filter_parent_entries(entries):
    """过滤存在父目录的条目"""
    normalized_dict = {}
    # 生成标准化路径映射（保留原始路径格式）
    for entry in entries:
        normalized = entry.replace('\\', '/').strip('/')
        normalized_dict[normalized] = entry

    # 创建标准化路径集合
    normalized_set = set(normalized_dict.keys())
    filtered = []

    for norm_path in normalized_set:
        # 忽略根目录
        if not norm_path:
            continue
        
        parts = norm_path.split('/')
        # 生成所有父目录路径
        parent_paths = ['/'.join(parts[:i+1]) for i in range(len(parts)-1)]
        
        # 检查是否存在父目录
        if not any(parent in normalized_set for parent in parent_paths):
            filtered.append(normalized_dict[norm_path])

    return filtered

def get_entries_to_delete(rar_path):
    """获取需要删除的条目列表（增强过滤版）"""
    try:
        cmd = [rar_exe_path, 'lb', rar_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, **get_silent_args())
    except subprocess.CalledProcessError as e:
        print(f"无法列出压缩包内容: {os.path.basename(rar_path)} - {str(e)}")
        return []
    
    raw_entries = result.stdout.splitlines()
    candidates = []
    
    for entry in raw_entries:
        normalized = entry.replace('\\', '/').strip('/')
        parts = [p for p in normalized.split('/') if p]
        if any(part in delete_patterns for part in parts):
            candidates.append(entry)
    
    # 去重并过滤存在父目录的条目
    unique_entries = list(set(candidates))
    return filter_parent_entries(unique_entries)

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
        
        return len(entries), matched

    except subprocess.CalledProcessError as e:
        error_msg = f"RAR命令执行失败: {str(e)}"
        if "Cannot find" in str(e):
            error_msg += "（可能因父目录已被删除）"
        raise Exception(error_msg)

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

def generate_csv_report(results, base_dir):
    """生成CSV报告（增强大数据处理）"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_name = f"RAR清理报告_{timestamp}.csv"
    csv_path = os.path.join(base_dir, csv_name)
    
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["压缩包名称", "相对路径", "绝对路径", "处理状态", "删除数量", "匹配模式", "错误信息"])
            
            for res in results:
                # 计算相对路径
                try:
                    relative_path = os.path.relpath(res.rar_path, base_dir)
                except ValueError:
                    # 如果无法计算相对路径（例如在不同驱动器上），使用绝对路径
                    relative_path = res.rar_path
                
                status = "成功" if res.success else "失败"
                patterns = ', '.join(res.patterns) if res.patterns else ""
                error = res.error_msg if res.error_msg else ""
                
                writer.writerow([
                    os.path.basename(res.rar_path),
                    relative_path,
                    res.rar_path,
                    status,
                    res.deleted_count,
                    patterns,
                    error
                ])
        
        print(f"CSV报告已生成: {csv_path}")
        return csv_path
    except Exception as e:
        print(f"生成CSV报告失败: {str(e)}")
        return None

def collect_rar_files(paths):
    """
    从给定的路径列表中收集所有RAR文件
    支持文件和文件夹路径
    """
    rar_files = []
    
    for path_str in paths:
        path = Path(path_str)
        
        if not path.exists():
            print(f"警告: 路径不存在: {path}")
            continue
            
        if path.is_file():
            # 如果是文件，检查是否为RAR文件
            if path.suffix.lower() == '.rar':
                rar_files.append(str(path))
                print(f"添加RAR文件: {path.name}")
            else:
                print(f"跳过非RAR文件: {path.name}")
                
        elif path.is_dir():
            # 如果是文件夹，递归搜索所有RAR文件
            try:
                dir_rar_count = 0
                for rar_path in path.rglob('*.rar'):
                    rar_files.append(str(rar_path))
                    dir_rar_count += 1
                print(f"在文件夹 '{path.name}' 中发现 {dir_rar_count} 个RAR文件")
            except Exception as e:
                print(f"扫描文件夹失败 '{path}': {str(e)}")
    
    return rar_files

def wait_for_exit():
    """等待用户按键退出"""
    if sys.platform.startswith('win'):
        # Windows系统
        print("\n程序执行完毕，按任意键退出...")
        import msvcrt
        msvcrt.getch()
    else:
        # 其他系统（如Linux、macOS）
        input("\n程序执行完毕，按回车键退出...")

def get_base_directory(paths):
    """确定CSV报告保存的基础目录"""
    if not paths:
        return os.getcwd()
    
    # 如果有多个路径，使用第一个路径的父目录
    first_path = Path(paths[0])
    if first_path.is_file():
        return str(first_path.parent)
    else:
        return str(first_path)

def main():
    try:
        # 使用argparse处理命令行参数，支持拖放操作
        parser = argparse.ArgumentParser(description='处理RAR压缩包')
        parser.add_argument('paths', nargs='*', help='要处理的文件或文件夹路径')
        args = parser.parse_args()
        
        # 如果没有提供路径参数，使用交互式输入
        if not args.paths:
            print("提示: 您可以直接将文件或文件夹拖放到此程序上，或手动输入路径")
            input_path = input("请拖放文件或文件夹到此处，或直接输入路径: ").strip().strip('"')
            if not input_path:
                print("未提供路径，程序退出")
                wait_for_exit()
                return
            target_paths = [input_path]
        else:
            target_paths = args.paths
        
        # 确定基础目录（用于保存CSV报告）
        base_dir = get_base_directory(target_paths)
        
        print("=" * 60)
        print("开始扫描RAR文件...")
        print("=" * 60)
        
        rar_files = collect_rar_files(target_paths)
        
        if not rar_files:
            print("未找到任何RAR文件，程序退出")
            wait_for_exit()
            return
            
        print(f"\n总共发现待处理RAR文件: {len(rar_files)}个")
        print("文件列表:")
        for i, rar_file in enumerate(rar_files, 1):
            print(f"  {i:2d}. {rar_file}")
        
        # 修改确认方式：按回车继续，其他键取消
        print(f"\n按回车键开始处理这 {len(rar_files)} 个文件，按其他任意键取消...")
        response = input()
        if response != "":
            print("用户取消操作")
            wait_for_exit()
            return
            
    except Exception as e:
        print(f"程序初始化错误: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印详细错误信息
        wait_for_exit()
        return
    
    # 原有的处理逻辑保持不变，但添加异常处理
    try:
        results = []
        
        # 使用tqdm进度条
        print("\n开始处理RAR文件...")
        with tqdm(rar_files, desc="处理压缩包", unit="file", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            for rar_path in pbar:
                try:
                    pbar.set_postfix(file=os.path.basename(rar_path)[:15])
                    
                    # 添加路径有效性验证
                    if not os.path.isfile(rar_path):
                        raise Exception("文件不存在或已被删除")
                    
                    # 调用处理函数
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

                # 使用ResultItem命名元组而不是字典
                results.append(ResultItem(
                    rar_path=rar_path,
                    success=success,
                    deleted_count=deleted_count,
                    error_msg=error_msg,
                    patterns=patterns
                ))

        # 生成控制台报告
        if REPORT_TYPE in ("console", "both"):
            generate_console_report(results)
        
        # 生成CSV报告
        csv_path = None
        if REPORT_TYPE in ("csv", "both"):
            csv_path = generate_csv_report(results, base_dir)
        
        if csv_path:
            print(f"\nCSV报告路径: {os.path.abspath(csv_path)}")
        
        # 显示处理摘要
        print("\n" + "="*60)
        print("处理结果摘要:")
        print("="*60)
        success_count = sum(1 for r in results if r.success and r.deleted_count > 0)
        skipped_count = sum(1 for r in results if r.success and r.deleted_count == 0)
        failed_count = sum(1 for r in results if not r.success)
        total_deleted = sum(r.deleted_count for r in results)
        
        print(f"成功处理并删除文件: {success_count} 个")
        print(f"无需处理: {skipped_count} 个")
        print(f"处理失败: {failed_count} 个")
        print(f"总共删除条目: {total_deleted} 个")
    
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 程序结束前等待用户按键
    wait_for_exit()

if __name__ == "__main__":
    main()