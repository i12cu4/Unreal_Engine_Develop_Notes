"""
RAR压缩包删除冗余文件工具
功能:删除RAR压缩包中的指定文件和文件夹
"""
import os
import subprocess
import tempfile
import shutil
from tqdm import tqdm

# ===================== 用户配置区域 =====================
rar_exe_path = r"C:\Program File\WinRAR\rar.exe" #注意,这里是rar,与其他脚本不同
target_dir = r"G:\agw"
delete_patterns = ["Saved", "Intermediate", "Build", "Binaries", ".vs", ".svn", "DerivedDataCache",
                   "Read me.rar", "更多免费软件素材1.jpg",
                   "首页-虚幻4资源站-淘宝网.url", "2d素材库-传奇素材包-素材免费下载.url", "2d素材库素材免费下载.url", "虚幻(UE)素材免费下载.url", "源码素材免费下载.url","CG3DA - 免费下载各类精品CG资源 .url",
                   "爱给网-2d素材库-免费下载.txt", "爱给网-虚幻(UE)-免费下载.txt", "爱给网-源码-免费下载.txt","UE4资源安装说明.txt","免责声明【必看】.txt","  UE多个高质量写实风景地貌场景模型_-传奇素材包-素材说明.txt"]  # 支持文件/文件夹列表
silent_mode = True  # 静默模式开关
# ======================================================

def get_silent_args():
    """获取静默模式参数"""
    if os.name == 'nt' and silent_mode:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return {'startupinfo': si}
    return {}

def check_rar_needs_processing(rar_path):
    """检查压缩包是否需要处理（是否存在需要删除的项）"""
    try:
        # 使用rar命令行工具列出压缩包内容
        cmd = [rar_exe_path, 'lb', rar_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, **get_silent_args())
    except subprocess.CalledProcessError as e:
        # 如果列出压缩包内容失败，打印错误信息并返回False
        print(f"无法列出压缩包内容: {os.path.basename(rar_path)} - {str(e)}")
        return False
    entries = result.stdout.splitlines()
    for entry in entries:
        # 将压缩包内容按路径分割
        parts = entry.replace('\\', '/').split('/')
        parts = [p for p in parts if p.strip() != '']  # 去除空字符串
        for part in parts:
            # 如果路径中包含需要删除的项，返回True
            if part in delete_patterns:
                return True
    # 如果没有需要删除的项，返回False
    return False

def process_rar(rar_path):
    """处理压缩包中的指定文件和文件夹"""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 解压命令
            extract_cmd = [
                rar_exe_path,
                'x', '-ibck', '-y',
                rar_path,
                temp_dir
            ]
            subprocess.run(extract_cmd, check=True, **get_silent_args())

            # 删除目标项统计
            deleted_files = 0
            deleted_dirs = 0
            matched_patterns = set()

            # 自下而上遍历（先处理深层内容）
            for root, dirs, files in tqdm(os.walk(temp_dir, topdown=False),
                                        desc="扫描内容", leave=False):
                # 处理文件
                for file in files:
                    if file in delete_patterns:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            deleted_files += 1
                            matched_patterns.add(file)
                        except Exception as e:
                            print(f"文件删除失败: {file_path} - {str(e)}")

                # 处理目录
                for dir in dirs:
                    if dir in delete_patterns:
                        dir_path = os.path.join(root, dir)
                        try:
                            shutil.rmtree(dir_path, ignore_errors=True)
                            deleted_dirs += 1
                            matched_patterns.add(dir)
                        except Exception as e:
                            print(f"目录删除失败: {dir_path} - {str(e)}")

            # 删除原压缩包
            os.remove(rar_path)

            # 重新压缩
            compress_cmd = [
                rar_exe_path,
                'a', '-r', '-ep1', '-df', '-ibck',
                rar_path,
                os.path.join(temp_dir, '*')
            ]
            subprocess.run(compress_cmd, check=True, **get_silent_args())

            return deleted_files, deleted_dirs, matched_patterns

        except subprocess.CalledProcessError as e:
            print(f"\n命令行操作失败: {str(e)}")
            raise

# 主程序
if __name__ == "__main__":
    # 收集所有RAR文件
    rar_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith('.rar'):
                rar_files.append(os.path.join(root, file))

    # 带进度条处理
    with tqdm(rar_files, desc="处理压缩包", unit="file") as pbar:
        for rar_path in pbar:
            pbar.set_postfix(file=os.path.basename(rar_path))
            try:
                # 检查是否需要处理
                needs_processing = check_rar_needs_processing(rar_path)
            except Exception as e:
                pbar.write(f"检查失败: {os.path.basename(rar_path)} - {str(e)}")
                continue
            if not needs_processing:
                pbar.write(f"跳过: {os.path.basename(rar_path)} (无匹配项)")
                continue
            try:
                files_count, dirs_count, matched_patterns = process_rar(rar_path)
                summary = []
                if files_count > 0:
                    summary.append(f"文件: {files_count}个")
                if dirs_count > 0:
                    summary.append(f"文件夹: {dirs_count}个")
                
                msg = f"成功处理: {os.path.basename(rar_path)}"
                if summary:
                    msg += f" ({', '.join(summary)})"
                else:
                    msg += " (无删除项)"
                if matched_patterns:
                    msg += f"，删除了匹配的模式: {', '.join(sorted(matched_patterns))}"
                pbar.write(msg)
            except Exception as e:
                pbar.write(f"处理失败: {os.path.basename(rar_path)} - {str(e)}")