# -*- coding: utf-8 -*-
import argostranslate.package
import argostranslate.translate
from tqdm import tqdm  # 进度条支持

def install_language_packages():
    """自动安装中英互译语言包（首次运行需要下载）"""
    
    # 更新可用包列表
    argostranslate.package.update_package_index()
    
    # 查找需要的中英互译包
    available_packages = argostranslate.package.get_available_packages()
    target_packages = [
        pkg for pkg in available_packages
        if (pkg.from_code == "zh" and pkg.to_code == "en") or 
           (pkg.from_code == "en" and pkg.to_code == "zh")
    ]

    # 下载并安装包
    for pkg in target_packages:
        print(f"正在安装 {pkg.from_code}->{pkg.to_code} 语言包...")
        download_path = pkg.download()
        argostranslate.package.install_from_path(download_path)

def is_chinese(text):
    """简单判断是否包含中文字符"""
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def auto_translate(text: str) -> str:
    """智能判断翻译方向：中文↔英文"""
    try:
        if is_chinese(text):
            return argostranslate.translate.translate(text, "zh", "en")
        else:
            return argostranslate.translate.translate(text, "en", "zh")
    except Exception as e:
        print(f"翻译错误: {str(e)}")
        return text  # 失败时返回原文

def batch_translate(texts: list) -> list:
    """批量翻译（自动检测语言）"""
    return [auto_translate(t) for t in texts]

if __name__ == "__main__":
    # 首次运行安装语言包（注释掉后续使用）
    # install_language_packages()  # 注意：首次需要联网下载
    
    print("="*40)
    print("离线英汉互译工具（Ctrl+C退出）")
    print("提示：请确保已安装语言包（首次需运行install_language_packages()）")
    print("="*40)
    
    while True:
        try:
            user_input = input("\n请输入文本（直接回车退出）:\n").strip()
            if not user_input:
                print("程序已退出。")
                break
            
            result = auto_translate(user_input)
            print("\n翻译结果：\n" + result)
            
        except KeyboardInterrupt:
            print("\n检测到中断，程序退出。")
            break
        except Exception as e:
            print(f"发生未知错误: {str(e)}")