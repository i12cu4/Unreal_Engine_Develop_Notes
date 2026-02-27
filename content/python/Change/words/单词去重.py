def remove_duplicates(input_string):
    words = input_string.split()
    unique_words = set(words)
    result_string = ' '.join(unique_words)
    return result_string

# 输入一串包含多个单词的字符串
input_string = input("请输入一串包含多个单词的字符串: ")

# 调用函数去重并输出结果
result = remove_duplicates(input_string)
print("去重后的结果:", result)
