import os
import re

# 定义映射文件和目标文件的绝对路径
key_path = r"content\python\执行文件\文本\字符串映射\key.txt"           #map 键的路径
value_path = r"content\python\执行文件\文本\字符串映射\value.txt"       #map 值的路径

files_to_process = [                                                 #替换map文本路径
    r"content\python\执行文件\文本\字符串映射\A.txt",
    r"content\python\执行文件\文本\字符串映射\B.txt",
    r"content\python\执行文件\文本\字符串映射\C.txt",
    r"content\python\执行文件\文本\字符串映射\D.txt"
]

def main():

    # 读取映射关系
    replacement_map = {}
    try:
        with open(key_path, 'r', encoding='utf-8') as key_file, \
             open(value_path, 'r', encoding='utf-8') as value_file:
            
            keys = key_file.read().splitlines()
            values = value_file.read().splitlines()
            
            if len(keys) != len(values):
                print(f"警告: key.txt({len(keys)}行)与value.txt({len(values)}行)行数不一致")
            
            # 构建映射字典（跳过空行）
            for k, v in zip(keys, values):
                if k.strip():  # 忽略空key
                    replacement_map[k] = v
    except Exception as e:
        print(f"读取映射文件失败: {str(e)}")
        return

    # 按key长度降序排序（避免短key先替换影响长key）
    sorted_keys = sorted(replacement_map.keys(), key=len, reverse=True)
    
    # 处理每个目标文件
    for file_path in files_to_process:
        try:
            # 读取原始文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 执行替换操作 - 修复特殊字符匹配问题
            for key in sorted_keys:
                # 使用更灵活的模式匹配特殊键
                pattern = r'(?<!\w)' + re.escape(key) + r'(?!\w)'
                content = re.sub(pattern, replacement_map[key], content)
            
            # 生成新文件名（添加后缀）
            base, ext = os.path.splitext(file_path)
            new_file_path = f"{base}_replaced{ext}"
            
            # 写入新文件
            with open(new_file_path, 'w', encoding='utf-8') as new_file:
                new_file.write(content)
            
            print(f"文件处理成功: {file_path} -> {new_file_path}")
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")

if __name__ == "__main__":
    main()