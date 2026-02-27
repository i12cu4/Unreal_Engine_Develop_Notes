from zhconv import convert

def is_traditional_chinese(text):
    """判断文本是否包含繁体字"""
    simplified = convert(text, 'zh-cn')
    return simplified != text  # 如果转换后内容不同则包含繁体字

def auto_convert(text):
    """智能转换简繁体"""
    if is_traditional_chinese(text):
        return convert(text, 'zh-cn')  # 繁转简
    else:
        return convert(text, 'zh-tw')  # 简转繁

def batch_convert(texts):
    """批量转换处理"""
    return [auto_convert(t) for t in texts]

if __name__ == '__main__':
    while True:
        user_input = input("请输入文本(输入空退出)：\n").strip()
        if user_input.lower() in (''):
            print("程序已退出。")
            break
        if user_input:
            print("转换结果：\n"+auto_convert(user_input))