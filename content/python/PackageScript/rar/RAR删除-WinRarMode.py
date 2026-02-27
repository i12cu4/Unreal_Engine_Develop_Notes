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
rar_exe_path = r"C:\Program File\WinRAR\WinRAR.exe"
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

def process_rar(rar_path):
    """处理RAR文件"""
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
                        except Exception as e:
                            print(f"文件删除失败: {file_path} - {str(e)}")

                # 处理目录
                for dir in dirs:
                    if dir in delete_patterns:
                        dir_path = os.path.join(root, dir)
                        try:
                            shutil.rmtree(dir_path, ignore_errors=True)
                            deleted_dirs += 1
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

            return deleted_files, deleted_dirs

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
                files_count, dirs_count = process_rar(rar_path)
                summary = []
                if files_count > 0:
                    summary.append(f"文件: {files_count}个")
                if dirs_count > 0:
                    summary.append(f"文件夹: {dirs_count}个")
                
                pbar.write(f"成功处理: {os.path.basename(rar_path)}"
                          f" ({', '.join(summary) if summary else '无删除项'})")
            except Exception as e:
                pbar.write(f"处理失败: {os.path.basename(rar_path)} - {str(e)}")