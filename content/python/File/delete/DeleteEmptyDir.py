import os
import send2trash

def find_and_remove_empty_folders(path):
    """
    深度遍历文件夹，查找并移动空文件夹到回收站
    """
    empty_folders = []
    
    # 深度优先遍历
    for root, dirs, files in os.walk(path, topdown=False):
        # 检查当前文件夹是否为空
        if not dirs and not files:
            empty_folders.append(root)
            print(f"找到空文件夹: {root}")
    
    # 移动空文件夹到回收站
    if empty_folders:
        print(f"\n共找到 {len(empty_folders)} 个空文件夹")
        confirm = input("是否要将这些空文件夹移动到回收站？(y/n): ").lower()
        
        if confirm == 'y':
            for folder in empty_folders:
                try:
                    send2trash.send2trash(folder)
                    print(f"已移动到回收站: {folder}")
                except Exception as e:
                    print(f"移动失败 {folder}: {e}")
        else:
            print("操作已取消")
    else:
        print("未找到空文件夹")

def main():
    # 设置要扫描的路径
    target_path = r"C:\Users\Administrator\Desktop\新建文件夹-251107-105946993\中华书局出版社精选500册"  # 请修改为你的实际路径
    
    # 检查路径是否存在
    if not os.path.exists(target_path):
        print(f"错误: 路径 '{target_path}' 不存在")
        return
    
    print(f"开始扫描路径: {target_path}")
    print("正在查找空文件夹...")
    
    find_and_remove_empty_folders(target_path)

if __name__ == "__main__":
    main()