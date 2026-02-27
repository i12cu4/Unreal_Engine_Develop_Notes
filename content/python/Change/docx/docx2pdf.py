#Word转Pdf
from comtypes.client import CreateObject
import os

def wd_to_pdf( folder):
    #word文档转化为pdf文档时使用的格式为17
    wdFormatPDF = 17
    wdToPDF = CreateObject("Word.Application")
    #获取指定目录下面的所有文件
    files = os.listdir(folder)
    # files = list_nohidden(folder)
    print(files)
    #获取word类型的文件放到一个列表里面
    wdfiles = [f for f in files if f.endswith((".doc", ".docx"))]
    #去除word生成的隐藏文件
    wdfiles2 = [f for f in wdfiles if not f.startswith('~') ]
    for wdfile in wdfiles2:
        #将word文件放到指定的路径下面
        wdPath = os.path.join(folder, wdfile)
        #设置将要存放pdf文件的路径
        pdfPath = wdPath.split(".")[0] + '.pdf'
        #判断是否已经存在对应的pdf文件，如果不存在就加入到存放pdf的路径内
        if pdfPath[-3:] != 'pdf':
            pdfPath = pdfPath + ".pdf"
        #将word文档转化为pdf文件，先打开word所在路径文件，然后在处理后保存pdf文件，最后关闭
        pdfCreate = wdToPDF.Documents.Open(wdPath)
        pdfCreate.SaveAs(pdfPath, wdFormatPDF)
        pdfCreate.Close()

wd_to_pdf(r'C:\Users\i12cu84\ocr')

