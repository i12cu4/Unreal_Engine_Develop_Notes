import os
import sys
import glob

def read_and_display_file(filepath):
    """读取并显示文本文件的内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"\n=== 文件内容: {os.path.basename(filepath)} ===")
            print(content)
            print("=" * (30 + len(os.path.basename(filepath))))
    except FileNotFoundError:
        print(f"错误: 文件 '{filepath}' 不存在")
    except PermissionError:
        print(f"错误: 没有权限读取文件 '{filepath}'")
    except UnicodeDecodeError:
        print(f"错误: 无法以UTF-8编码读取文件 '{filepath}'，尝试其他编码")
        try:
            with open(filepath, 'r', encoding='latin-1') as file:
                content = file.read()
                print(f"\n=== 文件内容: {os.path.basename(filepath)} ===")
                print(content)
                print("=" * (30 + len(os.path.basename(filepath))))
        except Exception as e:
            print(f"错误: 无法读取文件 '{filepath}': {e}")
    except Exception as e:
        print(f"错误: 读取文件 '{filepath}' 时发生异常: {e}")

def process_input(user_input):
    """处理用户输入"""
    # 去除输入字符串两端的引号（拖放文件时可能会添加）
    cleaned_input = user_input.strip().strip('"').strip("'")
    
    # 检查是否是退出命令
    if cleaned_input.lower() in ['exit', 'quit', 'q']:
        print("感谢使用，再见！")
        return False
    
    # 检查是否是帮助命令
    elif cleaned_input.lower() in ['help', '?']:
        print("\n=== 帮助信息 ===")
        print("1. 将txt文件拖放到此窗口即可显示文件内容")
        print("2. 输入 'exit', 'quit' 或 'q' 退出程序")
        print("3. 输入 'help' 或 '?' 显示此帮助信息")
        print("4. 支持通配符，如: *.txt")
        print("================\n")
        return True
    
    # 检查是否是文件或文件模式
    elif os.path.isfile(cleaned_input):
        # 单个文件
        read_and_display_file(cleaned_input)
        return True
    else:
        # 尝试使用通配符匹配文件
        matched_files = glob.glob(cleaned_input)
        if matched_files:
            for filepath in matched_files:
                if os.path.isfile(filepath):
                    read_and_display_file(filepath)
            return True
        else:
            print(f"未找到文件或命令: {cleaned_input}")
            print("输入 'help' 获取帮助信息")
            return True

def main():
    """主函数"""
    print("=== Python 文件阅读器 ===")
    print("将txt文件拖放到此窗口即可显示文件内容")
    print("输入 'help' 获取更多信息，输入 'exit' 退出程序")
    print("=" * 40)
    
    # 主循环
    while True:
        try:
            user_input = input("\n>>> ").strip()
            if not process_input(user_input):
                break
        except KeyboardInterrupt:
            print("\n\n检测到中断信号，程序退出。")
            break
        except EOFError:
            print("\n\n输入结束，程序退出。")
            break
        except Exception as e:
            print(f"\n发生未知错误: {e}")

if __name__ == "__main__":
    main()