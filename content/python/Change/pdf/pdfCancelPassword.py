import PyPDF2

# 读取原始PDF文件
with open('protected.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    
    # 验证密码（这里需要输入正确的密码）
    if reader.is_encrypted:
        print("The PDF is encrypted.")
        password = input("Enter the password for the PDF: ")
        reader.decrypt(password)
    
    # 创建PDF写入器对象
    writer = PyPDF2.PdfWriter()
    
    # 将页面添加到写入器对象中
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        writer.add_page(page)
    
    # 写入新的PDF文件，不加密
    with open('unprotected.pdf', 'wb') as output_pdf:
        writer.write(output_pdf)
        
print("New PDF file without password has been created.")
