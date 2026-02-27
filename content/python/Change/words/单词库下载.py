#读取指定路径txt 下载内容
import subprocess

def install_libraries_from_file(file_path):
    with open(file_path, 'r') as file:
        libraries = file.readlines()
        libraries = [lib.strip() for lib in libraries if lib.strip()]  # 去除空行并去除首尾空白字符

    for library in libraries:
        try:
            subprocess.check_call(['pip', 'install', library])
            print(f"Successfully installed {library}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {library}: {e}")

if __name__ == "__main__":
    file_path = r'C:\Users\chru\Desktop\libs.txt'
    install_libraries_from_file(file_path)