# pip install googletrans==4.0.0-rc1
from googletrans import Translator

translator = Translator()

def detect_language(text):
    """检测文本语言"""
    try:
        detection = translator.detect(text)
        return detection.lang
    except Exception as e:
        print(f"语言检测失败: {e}")
        return None

def auto_translate(text):
    """智能英汉互转"""
    try:
        lang = detect_language(text)
        if lang and lang.startswith('zh'):
            # 如果是中文则翻译成英文
            translated = translator.translate(text, dest='en')
        else:
            # 其他语言默认翻译成简体中文
            translated = translator.translate(text, dest='zh-cn')
        return translated.text
    except Exception as e:
        print(f"翻译过程中发生错误: {e}")
        return text  # 错误时返回原文

def batch_translate(texts):
    """批量转换处理"""
    return [auto_translate(t) for t in texts]

if __name__ == '__main__':
    print("提示：本程序需要联网使用，请确保网络连接正常")
    while True:
        user_input = input("\n请输入文本(输入空内容退出)：\n").strip()
        if not user_input:
            print("程序已退出。")
            break
        result = auto_translate(user_input)
        print("\n转换结果：\n" + result)