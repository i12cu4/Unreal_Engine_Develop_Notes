
#库

#函数

if __name__ == "__main__":
    HTML_DIR = r"C:\Users\chru\Desktop\merge"    # HTML文件所在目录

    fun(HTML_DIR)


->

import sys  # 添加这一行

#库

#函数

if __name__ == "__main__":
    HTML_DIR = sys.argv[1]  # 直接使用拖放的文件夹路径

    fun(HTML_DIR)

->

import sys
import os

print("=== 文件路径测试 ===")
print(f"共接收到 {len(sys.argv)-1} 个参数")

# 遍历所有拖动的文件/文件夹
for i, path in enumerate(sys.argv[1:], 1):
    path_type = "文件夹" if os.path.isdir(path) else "文件"
    print(f"{i}. {path} ({path_type})")

print("\n程序执行完毕，按回车键退出...")
input()




转译方案

if __name__ == "__main__":
    HTML_DIR = r"C:\Users\chru\Desktop\merge"    # HTML文件所在目录
    fun(HTML_DIR)

->

import sys  # 添加这一行
if __name__ == "__main__":
    HTML_DIR = sys.argv[1]  # 直接使用拖放的文件夹路径
    fun(HTML_DIR)