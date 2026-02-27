# 死循环查找指定路径文件并输出相关大小
import difflib


def readmarkdownfile(mdfilepath):
    """读取Markdown文件并返回文件信息列表"""
    fileinfolist = []
    with open(mdfilepath, "r", encoding="utf-8") as mdfile:
        lines = mdfile.readlines()
        # 跳过标题行
        for line in lines[2:]:
            parts = line.strip().split("|")
            if len(parts) > 3:
                # 清理空格并提取文件名和大小
                filename = parts[1].strip()
                sizekb = parts[2].strip()
                sizegb = parts[3].strip()
                fileinfolist.append((filename, sizekb, sizegb))
    return fileinfolist


def findmatches(searchstring, fileinfolist):
    """查找包含searchstring的所有文件信息"""
    matches = []
    for filename, sizekb, sizegb in fileinfolist:
        if searchstring.lower() in filename.lower():
            matches.append((filename, sizekb, sizegb))
    return matches


def checkstring(mdfilepaths, searchstring):
    for mdfilepath in mdfilepaths:
        mdfilepath = mdfilepath.strip()  # 清理空格
        fileinfolist = readmarkdownfile(mdfilepath)
        matches = findmatches(searchstring, fileinfolist)

        if matches:
            print(f"在文件 {mdfilepath} 中找到以下包含 '{searchstring}' 的文件：")
            for filename, sizekb, sizegb in matches:
                print(f"文件名: {filename}")
                print(f"文件大小 (KB): {sizekb}")
                print(f"文件大小 (GB): {sizegb}")
            print()  # 空行分隔
        else:
            print(f"在文件 {mdfilepath} 中没有找到包含该字符串的文件。")


mdfilepaths = [
    r"D:\Download\MovepackList\fileoutputE1.md",
    r"D:\Download\MovepackList\fileoutputE2.md",
    r"D:\Download\MovepackList\fileoutputE3.md",
    r"D:\Download\MovepackList\fileoutputE4.md",
]

while 1:
    searchstring = input()
    if searchstring == "":
        break
    checkstring(mdfilepaths, searchstring)
