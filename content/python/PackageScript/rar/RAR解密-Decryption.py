"""
RAR文件批量解密工具
功能：解密重新打包指定目录下的所有加密RAR文件
"""
import os
import subprocess
import logging
from tempfile import mkdtemp
import shutil

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ===================== 用户配置区域 =====================
TARGET_DIRECTORY = r"C:\Users\chru\Desktop\UE-VRGK-v2-master"  # 需要处理的目录
DECRYPTION_PASSWORD = "1234"                                  # 解密密码（需与加密密码一致）
OUTPUT_SUFFIX = "_decrypted"                                  # 新文件后缀
WINRAR_PATHS = [                                             # WinRAR可能安装路径
    r"C:\Program File\WinRAR\WinRar.exe"
]
# ======================================================

def find_winrar_executable() -> str:
    """查找可用的WinRAR执行路径"""
    for path in WINRAR_PATHS:
        if os.path.isfile(path):
            logger.info(f"找到WinRAR可执行文件: {path}")
            return path
    raise FileNotFoundError("未找到WinRAR，请检查安装路径或配置")

def find_rar_files(directory: str) -> list:
    """递归查找目录下的所有RAR文件"""
    rar_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".rar"):
                rar_files.append(os.path.join(root, file))
    logger.info(f"在 {directory} 中共找到 {len(rar_files)} 个RAR文件")
    return rar_files

def decrypt_rar_file(
    winrar_path: str,
    rar_path: str,
    output_suffix: str,
    password: str
) -> None:
    """解密单个RAR文件"""
    # 构建输出路径
    base, ext = os.path.splitext(rar_path)
    output_path = f"{base}{output_suffix}{ext}"
    
    # 创建临时工作目录
    temp_dir = mkdtemp()
    logger.debug(f"创建临时目录: {temp_dir}")

    try:
        # 带密码解压文件到临时目录
        logger.info(f"解压加密文件: {os.path.basename(rar_path)}")
        subprocess.run([
            winrar_path, "x", f"-p{password}", "-ibck", "-y", rar_path, f"{temp_dir}\\"
        ], check=True, stdout=subprocess.DEVNULL)

        # 无密码重新打包文件
        logger.info(f"创建解密文件: {os.path.basename(output_path)}")
        subprocess.run([
            winrar_path, "a", "-r", "-y", "-ep1",
            output_path, f"{temp_dir}\\*"
        ], check=True, stdout=subprocess.DEVNULL)

    except subprocess.CalledProcessError as e:
        logger.error(f"处理失败: {os.path.basename(rar_path)} - {str(e)}")
        raise
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"已清理临时目录: {temp_dir}")
        except Exception as e:
            logger.error(f"临时目录清理失败: {str(e)}")

def main():
    """主业务流程"""
    try:
        # 验证WinRAR路径
        winrar = find_winrar_executable()
        
        # 获取所有RAR文件
        files = find_rar_files(TARGET_DIRECTORY)
        
        # 批量处理文件
        for idx, rar_file in enumerate(files, 1):
            try:
                logger.info(f"正在处理文件 ({idx}/{len(files)})")
                decrypt_rar_file(winrar, rar_file, OUTPUT_SUFFIX, DECRYPTION_PASSWORD)
            except Exception as e:
                logger.error(f"文件处理中断: {rar_file} - {str(e)}")
                continue

    except Exception as e:
        logger.error(f"程序异常终止: {str(e)}", exc_info=True)
    finally:
        logger.info("处理流程执行完毕")

if __name__ == "__main__":
    # 提升日志级别显示调试信息
    logger.setLevel(logging.DEBUG)
    main()