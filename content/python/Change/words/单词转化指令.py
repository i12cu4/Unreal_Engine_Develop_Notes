def add_pip_install_prefix(input_string):
    words = input_string.split()
    result_lines = [f"!pip install {word}" for word in words]
    result_string = '\n'.join(result_lines)
    return result_string

# 输入一串包含多个单词的字符串
input_string = input("请输入一串包含多个单词的字符串: ")

# 调用函数添加前缀并输出结果
result = add_pip_install_prefix(input_string)
print("添加前缀后的结果:")
print(result)

#input:a b c

#output:
#!pip install a
#!pip install b
#!pip install c