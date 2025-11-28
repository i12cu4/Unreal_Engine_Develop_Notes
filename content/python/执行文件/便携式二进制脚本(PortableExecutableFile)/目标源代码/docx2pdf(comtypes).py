import sys
import os
import traceback

def install_comtypes():
    """安装必要的comtypes库"""
    try:
        import comtypes.client
        return True
    except ImportError:
        print("正在安装comtypes库...")
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "comtypes"])
            print("comtypes库安装成功!")
            return True
        except Exception as e:
            print(f"安装comtypes库失败: {e}")
            return False

# 确保comtypes库已安装
if not install_comtypes():
    input("按回车键退出...")
    sys.exit(1)

from comtypes.client import CreateObject

def word_to_pdf(word_path):
    """
    将单个Word文件转换为PDF
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(word_path):
            print(f"错误: 文件不存在 - {word_path}")
            return False
        
        # 检查文件扩展名
        if not word_path.lower().endswith(('.doc', '.docx')):
            print(f"错误: 文件不是Word格式 - {word_path}")
            return False
        
        # 生成输出PDF路径（同目录，同名）
        pdf_path = os.path.splitext(word_path)[0] + '.pdf'
        
        print(f"正在转换: {os.path.basename(word_path)}")
        print(f"输入文件: {word_path}")
        print(f"输出文件: {pdf_path}")
        
        # Word文档转化为PDF文档时使用的格式为17
        wdFormatPDF = 17
        
        # 创建Word应用程序实例
        print("正在启动Word应用程序...")
        word_app = CreateObject("Word.Application")
        word_app.Visible = False  # 不显示Word界面
        
        try:
            # 打开Word文档并转换为PDF
            print("正在打开Word文档...")
            doc = word_app.Documents.Open(os.path.abspath(word_path))
            print("正在转换为PDF...")
            doc.SaveAs(os.path.abspath(pdf_path), wdFormatPDF)
            doc.Close()
            print("✓ 转换完成!")
            return True
            
        except Exception as e:
            print(f"转换过程中出现错误: {str(e)}")
            traceback.print_exc()
            return False
            
        finally:
            # 确保Word应用程序被关闭
            print("正在关闭Word应用程序...")
            word_app.Quit()
            
    except Exception as e:
        print(f"初始化Word应用程序时出现错误: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """
    主函数 - 处理拖放的文件
    """
    try:
        if len(sys.argv) < 2:
            print("请将Word文件(.doc或.docx)拖放到此程序上")
            print("程序将在同目录下生成同名的PDF文件")
            input("按回车键退出...")
            return
        
        # 获取拖放的文件路径（处理可能包含空格的情况）
        file_path = sys.argv[1].strip('"')
        
        print("=" * 50)
        print(f"开始处理文件: {file_path}")
        
        if word_to_pdf(file_path):
            print(f"\nPDF文件已生成: {os.path.splitext(file_path)[0] + '.pdf'}")
        else:
            print("\n转换失败，请检查文件格式和权限")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        traceback.print_exc()
    
    input("按回车键退出...")

if __name__ == "__main__":
    main()