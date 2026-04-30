"""
CheckMissing.py - 双向检查（大小写不敏感版本）
1. 找出 URL 列表中缺失下载的仓库
2. 找出 ZIP 目录中多余的 ZIP 文件
匹配时忽略大小写，例如 "Owner/Repo" 可匹配 "owner_repo.zip"。
"""

import os
from pathlib import Path
from collections import defaultdict

# ==================== 用户配置区域 ====================
INPUT_FILE = r"D:\0lib2\All.txt"      # GitHub URL 列表
ZIP_ROOT = r"D:\0libZip"              # ZIP 文件存放目录
OUTPUT_MISSING = r"D:\0lib2\miss.txt" # 缺失仓库输出文件
OUTPUT_EXTRA = r"D:\0lib2\extra.txt"  # 多余 ZIP 文件输出文件
VERBOSE = False                       # 是否打印详细匹配过程
# ====================================================

def get_zip_prefix(url: str) -> str:
    """
    从 GitHub URL 提取 owner_repo 前缀（返回小写形式用于匹配）
    例如：https://github.com/11cafe/jaaz -> "11cafe_jaaz"
    """
    url = url.strip()
    if url.endswith('.git'):
        url = url[:-4]
    prefix = 'https://github.com/'
    if not url.startswith(prefix):
        raise ValueError(f"URL 不以 {prefix} 开头: {url}")
    repo_path = url[len(prefix):]  # "owner/repo"
    # 返回小写前缀，用于匹配
    return repo_path.replace('/', '_').lower()

def get_prefix_from_zipname(zip_name: str) -> str:
    """
    从 ZIP 文件名提取 owner_repo 前缀（返回小写形式用于匹配）。
    支持格式：
      - {owner}_{repo}@{sha}.zip
      - {owner}_{repo}.zip
    如果无法解析返回 None。
    """
    if not zip_name.endswith('.zip'):
        return None
    base = zip_name[:-4]
    # 如果包含 '@'，取 '@' 之前的部分
    if '@' in base:
        prefix = base.split('@')[0]
    else:
        prefix = base
    # 简单验证：必须包含至少一个 '_'
    if '_' not in prefix or '/' in prefix or '\\' in prefix:
        return None
    return prefix.lower()

def read_repo_urls(file_path: Path):
    """读取 URL 文件，返回去重后保持顺序的 URL 列表，并打印重复警告"""
    urls_ordered = []
    seen = set()
    duplicates = defaultdict(list)

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line in seen:
                duplicates[line].append(line_num)
            else:
                seen.add(line)
                urls_ordered.append(line)

    if duplicates:
        print("警告：输入文件中存在重复的 URL（已自动去重）")
        for url, lines in duplicates.items():
            print(f"  {url} 出现于行: {', '.join(map(str, lines))}")

    return urls_ordered

def main():
    input_path = Path(INPUT_FILE)
    zip_root = Path(ZIP_ROOT)
    output_missing = Path(OUTPUT_MISSING)
    output_extra = Path(OUTPUT_EXTRA)

    if not input_path.is_file():
        print(f"错误: 输入文件不存在: {input_path}")
        return
    if not zip_root.is_dir():
        print(f"错误: ZIP 根目录不存在: {zip_root}")
        return

    # 1. 读取 URL 列表，建立 小写前缀 -> 原始URL 的映射（注意：多个不同大小写的URL可能映射到同一个小写前缀）
    urls = read_repo_urls(input_path)
    if not urls:
        print("警告: 输入文件中没有有效的 URL。")
        return

    url_to_prefix_lower = {}
    prefix_lower_to_urls = defaultdict(list)  # 一个小写前缀可能对应多个原始URL（大小写不同）
    for url in urls:
        try:
            prefix_lower = get_zip_prefix(url)
            url_to_prefix_lower[url] = prefix_lower
            prefix_lower_to_urls[prefix_lower].append(url)
        except ValueError as e:
            print(f"跳过无效 URL: {url} - {e}")

    expected_prefixes_lower = set(prefix_lower_to_urls.keys())
    print(f"从 URL 列表解析到 {len(expected_prefixes_lower)} 个唯一仓库前缀（不区分大小写）")

    # 2. 扫描 ZIP 目录，提取所有 ZIP 文件及其小写前缀
    all_zip_files = list(zip_root.glob("*.zip"))
    print(f"ZIP 目录中共有 {len(all_zip_files)} 个 ZIP 文件")

    zip_prefix_lower_to_files = defaultdict(list)  # 小写前缀 -> 原始文件名列表
    orphan_zips = []  # 无法解析前缀的 ZIP 文件

    for zip_path in all_zip_files:
        zip_name = zip_path.name
        prefix_lower = get_prefix_from_zipname(zip_name)
        if prefix_lower is None:
            orphan_zips.append(zip_name)
        else:
            zip_prefix_lower_to_files[prefix_lower].append(zip_name)

    existing_prefixes_lower = set(zip_prefix_lower_to_files.keys())
    print(f"从 ZIP 文件解析到 {len(existing_prefixes_lower)} 个唯一仓库前缀（不区分大小写）")

    # 3. 计算缺失和多余（基于小写前缀）
    missing_prefixes_lower = expected_prefixes_lower - existing_prefixes_lower
    extra_prefixes_lower = existing_prefixes_lower - expected_prefixes_lower

    # 收集缺失的 URL（原始 URL，对于缺失前缀，可能对应多个大小写变体，全部输出）
    missing_urls = []
    for prefix_lower in missing_prefixes_lower:
        missing_urls.extend(prefix_lower_to_urls[prefix_lower])

    # 收集多余的 ZIP 文件（所有属于多余前缀的文件）
    extra_zip_files = []
    for prefix_lower in extra_prefixes_lower:
        extra_zip_files.extend(zip_prefix_lower_to_files[prefix_lower])

    # 4. 输出结果
    with open(output_missing, 'w', encoding='utf-8') as f:
        for url in missing_urls:
            f.write(url + '\n')

    with open(output_extra, 'w', encoding='utf-8') as f:
        for zip_name in extra_zip_files:
            f.write(zip_name + '\n')
        if orphan_zips:
            f.write("\n# 无法解析前缀的 ZIP 文件（命名不规范）:\n")
            for zip_name in orphan_zips:
                f.write(zip_name + '\n')

    # 打印统计
    print("\n========== 检查结果（忽略大小写） ==========")
    print(f"URL 列表中的唯一仓库前缀数: {len(expected_prefixes_lower)}")
    print(f"ZIP 目录中的唯一仓库前缀数: {len(existing_prefixes_lower)}")
    print(f"缺失的仓库数量: {len(missing_urls)}")
    print(f"多余的仓库数量: {len(extra_prefixes_lower)}")
    if orphan_zips:
        print(f"无法解析的 ZIP 文件数量: {len(orphan_zips)}")

    if missing_urls:
        print(f"缺失列表已保存至: {output_missing}")
    else:
        print("所有 URL 对应的仓库均存在 ZIP 文件（忽略大小写）。")

    if extra_zip_files:
        print(f"多余 ZIP 文件列表已保存至: {output_extra}")
        print("\n多余 ZIP 文件详情（可能是不在 URL 列表中的仓库）:")
        for zip_name in extra_zip_files:
            print(f"  - {zip_name}")
    else:
        print("没有发现多余的 ZIP 文件。")

    if orphan_zips:
        print("\n无法解析前缀的 ZIP 文件（请检查命名是否符合 {owner}_{repo}[@{sha}].zip 格式）:")
        for zip_name in orphan_zips:
            print(f"  - {zip_name}")

    if VERBOSE:
        print("\n========== 详细匹配 ==========")
        for prefix_lower in sorted(expected_prefixes_lower):
            if prefix_lower in existing_prefixes_lower:
                files = zip_prefix_lower_to_files[prefix_lower]
                print(f"✓ {prefix_lower} -> {', '.join(files)}")
            else:
                print(f"✗ {prefix_lower} (缺失)")
        for prefix_lower in sorted(extra_prefixes_lower):
            files = zip_prefix_lower_to_files[prefix_lower]
            print(f"⚠ 多余仓库 {prefix_lower} -> {', '.join(files)}")

if __name__ == '__main__':
    main()