# 以markdown的表格形式升序输出每一个文件夹中每一个文件
import os


def getfileinfo(path):
    """获取指定路径下的所有文件信息（包括子目录中的文件）"""
    fileinfolist = []
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            filesize = os.path.getsize(filepath)
            fileinfolist.append((file, filesize))
    return fileinfolist


def formatsize(sizeinbytes):
    """将字节大小转换为KB，并且每3个数用逗号隔开"""
    sizeinkb = sizeinbytes / 1024
    return "{:,.3f} KB".format(sizeinkb)


def formatgbsize(sizeinbytes):
    """将字节大小转换为GB，并四舍五入到小数点后一位"""
    sizeingb = sizeinbytes / (1024**3)
    return "{:.1f} GB".format(sizeingb)


def writetomarkdown(fileinfolist, outputfile):
    """将文件信息写入Markdown文件，包含文件大小KB和GB"""
    # 按文件大小升序排序
    fileinfolist.sort(key=lambda x: x[1])

    with open(outputfile, "w", encoding="utf-8") as mdfile:
        mdfile.write("| 文件名 | 文件大小 (KB) | 文件大小 (GB) |\n")
        mdfile.write("| ------ | -------------- | -------------- |\n")

        # 写入文件信息
        for filename, filesize in fileinfolist:
            formattedsizekb = formatsize(filesize)
            formattedsizegb = formatgbsize(filesize)
            mdfile.write(f"| {filename} | {formattedsizekb} | {formattedsizegb} |\n")


# 使用示例
if __name__ == "__main__":
    path_to_scan = r"E:\compare"
    output_md_file = r"D:\Download\fileoutputE4.md"
    fileinfolist = getfileinfo(path_to_scan)
    writetomarkdown(fileinfolist, output_md_file)
    print(f"文件信息已写入到 {output_md_file}")
