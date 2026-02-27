import os

def delete_files_with_unsupported_extensions(root_path):
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if os.path.splitext(file)[1].lower() not in ['.c', '.cpp', '.h', '.hpp']:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f'Deleted file: {file_path}')

# 指定要清理的目录路径
root_path = r'C:\Users\chru\Desktop\temp'

# 调用函数
delete_files_with_unsupported_extensions(root_path)
