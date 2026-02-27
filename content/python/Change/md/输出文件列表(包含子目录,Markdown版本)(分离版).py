# 以markdown的表格形式升序输出每一个文件夹中每一个文件(文件夹以表格形式分离)
import os


def getfileinfo(path):
    """获取指定路径下的所有文件信息（包括子目录中的文件）"""
    fileinfolist = {}
    for root, dirs, files in os.walk(path):
        # 将根目录替换为空字符串以便在Markdown中正确表示
        root_display = root.replace(path, "").strip(os.sep)
        fileinfolist[root_display] = [
            (file, os.path.getsize(os.path.join(root, file))) for file in files
        ]
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
    """将文件信息写入Markdown文件"""
    with open(outputfile, "w") as mdfile:
        # 写入根目录下的文件信息
        root_files = sorted(fileinfolist.get("", []), key=lambda x: x[1])
        mdfile.write("## 根目录文件信息\n")
        mdfile.write("| 文件名 | 文件大小 (KB) | 文件大小 (GB) |\n")
        mdfile.write("|--------|--------------:|--------------:|\n")
        for filename, filesize in root_files:
            formattedsizekb = formatsize(filesize)
            formattedsizegb = formatgbsize(filesize)
            mdfile.write(
                "| {} | {} | {} |\n".format(filename, formattedsizekb, formattedsizegb)
            )
        mdfile.write("\n")

        # 写入子目录下的文件信息
        for root_display, files in fileinfolist.items():
            if root_display:  # 跳过根目录，因为它已经被处理过了
                mdfile.write("## 目录 {} 文件信息\n".format(root_display))
                mdfile.write("| 文件名 | 文件大小 (KB) | 文件大小 (GB) |\n")
                mdfile.write("|--------|--------------:|--------------:|\n")
                for filename, filesize in sorted(files, key=lambda x: x[1]):
                    formattedsizekb = formatsize(filesize)
                    formattedsizegb = formatgbsize(filesize)
                    mdfile.write(
                        "| {} | {} | {} |\n".format(
                            filename, formattedsizekb, formattedsizegb
                        )
                    )
                mdfile.write("\n")


# 使用示例
if __name__ == "__main__":
    pathtoscan = r"D:\Download\task"
    outputmdfile = r"D:\Download\fileoutput_sep.md"
    fileinfolist = getfileinfo(pathtoscan)
    writetomarkdown(fileinfolist, outputmdfile)
    print(f"文件信息已写入到 {outputmdfile}")
