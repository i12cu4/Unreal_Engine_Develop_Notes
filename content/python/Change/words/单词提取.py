#Successfully 与 Failed 中提取失败库名字
def extract_failed_libraries(long_string):
    failed_libraries = []
    lines = long_string.strip().splitlines()  # 去除首尾空白字符并将长串字符串拆分为行
    for line in lines:
        if line.startswith('Failed'):
            words = line.split()
            if len(words) >= 4:
                failed_library = words[3].rstrip(':')
                failed_libraries.append(failed_library)
    return ' '.join(failed_libraries)

if __name__ == "__main__":
    long_string = """
Successfully installed scapy
Successfully installed inbox
Failed to install awesome-sphinxdoc: Command '['pip', 'install', 'awesome-sphinxdoc']' returned non-zero exit status 1.
Failed to install django-socketio: Command '['pip', 'install', 'django-socketio']' returned non-zero exit status 1.
    """
    failed_libraries = extract_failed_libraries(long_string)
    print(failed_libraries)

#output: awesome-sphinxdoc django-socketio