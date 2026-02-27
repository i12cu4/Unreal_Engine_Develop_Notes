import os
import string

# 获取当前目录下的所有.txt文件
txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]

# 编码格式 作示例
encoded_format="Y)m¯f/N*SgNÏvW0e¹ÿQúN_YY}"
encoded_format="^y^4ÿOFVàN:gÐNSVàÙNY}^"
encoded_format="[¹f«T0bNìs°W(kcW(e6ÆettÙNy^4Y}"
encoded_format="^0"
encoded_format="vOá"
encoded_format="ÿ·SÖfôYO(Dnc¨P0"

# 遍历所有.txt文件
for file in txt_files:
    # 读取文件内容
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查文件内容是否包含特定编码格式
    if encoded_format in content:
        # 删除特定编码的文本
        content = content.replace(encoded_format, '')

        # 写入到文件
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"文件{file}中的特定编码格式已删除。")

print("操作完成。")
