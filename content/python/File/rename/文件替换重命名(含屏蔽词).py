#文件替换重命名
import os

# 定义屏蔽词、替换目标和替换内容
not_word = "金请夏"
first_word = "请夏"
second_word = "金请夏"

# 指定文件路径
path = r"C:\Users\chru\Downloads\Cache\Cache"


# 遍历文件夹中的所有文件
for filename in os.listdir(path):
    # 检查文件名是否包含屏蔽词
    if not_word in filename:
        # 如果包含屏蔽词，则跳过
        continue
    elif first_word in filename:
        # 如果不包含屏蔽词，则进行替换
        new_filename = filename.replace(first_word, second_word)
        # 打印新的文件名
        print(f"旧文件名： {filename}, 新文件名： {new_filename}")
        # 你可以选择是否重命名文件
        # 如果要重命名，请取消下面两行的注释
        os.rename(os.path.join(path, filename), os.path.join(path, new_filename))
    else:
        # 如果既不包含关键词也不包含替换目标，则直接跳过
        continue
