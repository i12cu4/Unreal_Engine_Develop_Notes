import os
import shutil
import stat
import csv
from datetime import datetime
import sys

# 全局变量记录操作详情
copied_files = []
overwritten_files = []
skipped_files = []

def get_usb_root_path():
    """获取U盘根目录路径 - 修复打包后路径问题"""
    try:
        # 方法1: 通过当前执行文件路径获取
        if getattr(sys, 'frozen', False):
            # 打包后的exe文件
            exe_path = os.path.dirname(sys.executable)
            # 获取驱动器根目录
            drive = os.path.splitdrive(exe_path)[0] + '\\'
            return drive
        else:
            # 脚本模式
            script_path = os.path.dirname(os.path.abspath(__file__))
            drive = os.path.splitdrive(script_path)[0] + '\\'
            return drive
    except Exception as e:
        print(f"获取U盘路径时出错: {e}")
        # 方法2: 尝试通过工作目录获取
        try:
            cwd = os.getcwd()
            drive = os.path.splitdrive(cwd)[0] + '\\'
            return drive
        except:
            # 方法3: 默认返回E盘（常见的U盘盘符）
            return "E:\\"

def should_overwrite(src, dst):
    """判断是否需要覆盖文件：只有当源文件比目标文件新或大小不同时才覆盖"""
    if not os.path.exists(dst):
        return True  # 目标文件不存在，需要复制
    
    try:
        # 获取文件信息
        src_stat = os.stat(src)
        dst_stat = os.stat(dst)
        
        # 如果源文件比目标文件新，或者文件大小不同，则需要覆盖
        if src_stat.st_mtime > dst_stat.st_mtime or src_stat.st_size != dst_stat.st_size:
            return True
    except OSError:
        # 如果无法获取文件信息，默认需要覆盖
        return True
    
    return False  # 文件相同，不需要覆盖

def copy_with_check(src, dst, relative_path):
    """复制文件，检查是否需要覆盖"""
    try:
        file_exists = os.path.exists(dst)
        
        if file_exists:
            # 检查是否需要覆盖
            if should_overwrite(src, dst):
                # 如果目标文件存在且为只读，先清除只读属性
                try:
                    os.chmod(dst, stat.S_IWRITE)
                except:
                    pass
                
                shutil.copy2(src, dst)
                print(f"覆盖: {relative_path}")
                overwritten_files.append(relative_path)
                return "overwrite"
            else:
                # 文件相同，跳过
                skipped_files.append(relative_path)
                return "skip"
        else:
            # 目标文件不存在，直接复制
            shutil.copy2(src, dst)
            print(f"复制: {relative_path}")
            copied_files.append(relative_path)
            return "copy"
            
    except Exception as e:
        print(f"操作失败 {relative_path}: {e}")
        return "error"

def sync_folders(source, destination):
    """同步两个文件夹：只复制或覆盖需要更新的文件"""
    global copied_files, overwritten_files, skipped_files
    copied_files = []
    overwritten_files = []
    skipped_files = []
    error_files = 0
    
    # 确保目标文件夹存在
    if not os.path.exists(destination):
        os.makedirs(destination)
        print(f"创建目标文件夹: {destination}")
    
    # 遍历源文件夹
    for root, dirs, files in os.walk(source):
        # 计算相对路径
        rel_path = os.path.relpath(root, source)
        if rel_path == '.':
            rel_path = ''
        
        # 在目标文件夹中创建对应的子目录
        dest_dir = os.path.join(destination, rel_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        # 复制文件
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)
            file_rel_path = os.path.join(rel_path, file) if rel_path else file
            
            # 执行复制/覆盖/跳过操作
            result = copy_with_check(src_file, dest_file, file_rel_path)
            if result == "error":
                error_files += 1
            elif result == "skip":
                # 跳过文件不显示，避免输出过多
                pass
    
    return len(copied_files), len(overwritten_files), len(skipped_files), error_files

def get_desktop_path():
    """获取Windows桌面路径"""
    try:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        if os.path.exists(desktop):
            return desktop
        
        user_profile = os.environ.get('USERPROFILE', '')
        if user_profile:
            desktop = os.path.join(user_profile, 'Desktop')
            if os.path.exists(desktop):
                return desktop
        
        return None
    except Exception as e:
        print(f"获取桌面路径时出错: {e}")
        return None

def create_csv_log(usb_root_path, copied_files, overwritten_files, skipped_files, source_lib, target_lib):
    """创建CSV日志文件，记录复制、覆盖和跳过的文件，按操作类型分类"""
    try:
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"lib_sync_log_{timestamp}.csv"
        csv_path = os.path.join(usb_root_path, csv_filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['操作类型', '相对路径', '源文件绝对路径', '目标文件绝对路径', '时间戳']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # 写入表头
            writer.writeheader()
            
            # 先写入复制文件记录
            if copied_files:
                writer.writerow({'操作类型': '=== 复制文件列表 ===', '相对路径': '', '源文件绝对路径': '', '目标文件绝对路径': '', '时间戳': ''})
                for file in copied_files:
                    src_abs_path = os.path.join(source_lib, file)
                    dst_abs_path = os.path.join(target_lib, file)
                    writer.writerow({
                        '操作类型': '复制',
                        '相对路径': file,
                        '源文件绝对路径': src_abs_path,
                        '目标文件绝对路径': dst_abs_path,
                        '时间戳': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            # 再写入覆盖文件记录
            if overwritten_files:
                writer.writerow({'操作类型': '=== 覆盖文件列表 ===', '相对路径': '', '源文件绝对路径': '', '目标文件绝对路径': '', '时间戳': ''})
                for file in overwritten_files:
                    src_abs_path = os.path.join(source_lib, file)
                    dst_abs_path = os.path.join(target_lib, file)
                    writer.writerow({
                        '操作类型': '覆盖',
                        '相对路径': file,
                        '源文件绝对路径': src_abs_path,
                        '目标文件绝对路径': dst_abs_path,
                        '时间戳': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            # 最后写入跳过文件记录
            if skipped_files:
                writer.writerow({'操作类型': '=== 跳过文件列表 ===', '相对路径': '', '源文件绝对路径': '', '目标文件绝对路径': '', '时间戳': ''})
                for file in skipped_files:
                    src_abs_path = os.path.join(source_lib, file)
                    dst_abs_path = os.path.join(target_lib, file)
                    writer.writerow({
                        '操作类型': '跳过',
                        '相对路径': file,
                        '源文件绝对路径': src_abs_path,
                        '目标文件绝对路径': dst_abs_path,
                        '时间戳': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        print(f"\n操作日志已保存到: {csv_path}")
        return csv_path
    except Exception as e:
        print(f"创建CSV日志时出错: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("           桌面lib文件夹同步工具")
    print("=" * 60)
    print("功能: 将桌面lib文件夹的内容同步到U盘lib文件夹")
    print("注意:")
    print("  - 只会覆盖U盘中与桌面同名且已更改的文件")
    print("  - U盘中独有的文件将保持不变")
    print("  - 桌面lib中新增的文件会被复制到U盘")
    print("  - 相同的文件将跳过，不进行任何操作")
    print("-" * 60)
    
    # 获取路径
    desktop_path = get_desktop_path()
    usb_root_path = get_usb_root_path()
    
    if not desktop_path:
        print("错误: 无法找到桌面路径!")
        input("按回车键退出...")
        return
    
    source_lib = os.path.join(desktop_path, 'lib')
    target_lib = os.path.join(usb_root_path, 'lib')
    
    print(f"源路径: {source_lib}")
    print(f"目标路径: {target_lib}")
    print("-" * 60)
    
    # 检查源文件夹是否存在
    if not os.path.exists(source_lib):
        print(f"错误: 桌面上找不到 'lib' 文件夹!")
        input("按回车键退出...")
        return
    
    # 修改确认方式：按回车继续，其他键取消
    print("按回车键开始同步，按其他任意键取消...")
    response = input()
    if response != "":
        print("操作已取消")
        input("按回车键退出...")
        return
    
    # 执行同步
    print("开始同步...\n")
    copied_count, overwritten_count, skipped_count, error_count = sync_folders(source_lib, target_lib)
    
    # 显示详细结果
    print("\n" + "=" * 60)
    print("同步完成!")
    print(f"复制文件: {copied_count} 个")
    print(f"覆盖文件: {overwritten_count} 个")
    print(f"跳过文件: {skipped_count} 个")
    print(f"错误文件: {error_count} 个")
    
    # 显示复制的文件列表
    if copied_files:
        print("\n复制的文件:")
        for file in copied_files:
            print(f"  + {file}")
    
    # 显示覆盖的文件列表
    if overwritten_files:
        print("\n覆盖的文件:")
        for file in overwritten_files:
            print(f"  * {file}")
    
    # 显示跳过的文件列表
    """
    if skipped_files:
        print("\n跳过的文件:")
        for file in skipped_files:
            print(f"  - {file}")
    """
    # 创建CSV日志
    csv_path = create_csv_log(usb_root_path, copied_files, overwritten_files, skipped_files, source_lib, target_lib)
    
    if error_count > 0:
        print("\n注意: 有文件操作失败，请检查权限或文件是否被占用")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()