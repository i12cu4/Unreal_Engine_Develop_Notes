import os
import shutil

# 需要删除的文件夹列表
folders_to_remove = ['.vs', 'Binaries', 'Intermediate', 'Saved','DerivedDataCache','Build','Platforms']

# 遍历并删除文件夹
for folder in folders_to_remove:
    target_path = os.path.join(os.getcwd(), folder)  # 获取当前目录下的目标路径
    if os.path.exists(target_path) and os.path.isdir(target_path):
        try:
            shutil.rmtree(target_path)
            print(f"成功删除文件夹: {folder}")
        except Exception as e:
            print(f"删除失败: {folder} - 错误信息: {str(e)}")
    else:
        print(f"文件夹不存在: {folder}，跳过删除")

print("\n操作执行完毕，窗口将在10秒后自动关闭...")
os.system("timeout /t 10 /nobreak >nul")  # 仅Windows生效