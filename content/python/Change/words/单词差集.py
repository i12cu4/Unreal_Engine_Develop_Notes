# 读取A.txt文件中的所有单词，并存入集合中
with open('A.txt', 'r', encoding='utf-8') as file:
    words_set = set(line.strip() for line in file)

# 读取B.txt文件，并过滤掉在集合中的单词
with open('B.txt', 'r', encoding='utf-8') as file, \
     open('C.txt', 'w', encoding='utf-8') as output_file:
    for line in file:
        word = line.strip()
        # 如果单词不在A.txt的集合中，则写入到C.txt文件中
        if word not in words_set:
            output_file.write(line)
