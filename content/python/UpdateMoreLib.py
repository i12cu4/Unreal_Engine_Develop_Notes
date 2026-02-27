import os

# 获取过期库列表
outdated_packages = os.popen('pip list --outdated --format=freeze').read().split('\n')

# 更新每个过期库
for package in outdated_packages:
    if package:
        package_name = package.split('==')[0]
        os.system(f'pip install --upgrade {package_name}')
