# GitHub 仓库批量 ZIP 下载与完整性检查工具
GitHub Repo Batch ZIP Downloader & Integrity Checker
本仓库提供了一套完整的 Python 工具，用于**批量下载 GitHub 仓库的 ZIP 压缩包**（自动检测最新版本、支持断点续传、旧版本清理）以及**双向检查下载完整性**（找出缺失的仓库和多余的 ZIP 文件）。适用于需要离线备份、批量归档 GitHub 仓库的场景。

## ✨ 功能特点

### 📦 批量下载工具（`StartDownload.py`）
- ✅ 支持从文本文件批量读取 GitHub 仓库 URL
- ✅ **自动检测最新版本**：通过 GitHub API 获取默认分支的最新 commit SHA
- ✅ **智能跳过已下载**：本地已存在最新版本文件时自动跳过
- ✅ **旧版本自动清理**：当仓库更新后，旧版本 ZIP 自动移至 `old_versions/` 目录
- ✅ **手动文件识别**：即使手动放入符合命名规则的 ZIP 文件，也能被识别并跳过重复下载
- ✅ **失败重试机制**：网络波动、超时等可重试错误自动重试（最多 3 次）
- ✅ **GitHub Token 支持**：可配置环境变量或 `.github_token` 文件以提高 API 限额
- ✅ **进度可视化**：自动使用 `tqdm` 显示下载进度（若已安装）
- ✅ **原子化状态保存**：配置文件安全更新，避免数据损坏
- ✅ **详细日志**：所有操作记录到 `zip_download_log.txt`

### 🔍 完整性检查工具（`CheckMissing.py`）
- ✅ **双向检查**：
  - 检查 URL 列表中有哪些仓库尚未下载（缺失）
  - 检查 ZIP 目录中有哪些 ZIP 文件不在 URL 列表中（多余）
- ✅ **大小写不敏感匹配**：`Owner/Repo` 可以匹配 `owner_repo@sha.zip` 或 `OWNER_REPO.zip`
- ✅ **支持两种 ZIP 命名格式**：
  - `{owner}_{repo}@{short_sha}.zip`（下载工具默认格式）
  - `{owner}_{repo}.zip`（手动命名兼容）
- ✅ **自动去重**：输入文件中重复的 URL 会被自动去重并给出警告
- ✅ **输出清晰报告**：分别生成缺失列表和多余文件列表

## 📁 文件结构
```
├── StartDownload.py # 主下载程序（推荐使用）
├── GitHubZipDownloader.py # 备选下载程序（功能相同，版本略有差异）
├── CheckMissing.py # 完整性检查工具
├── README.md # 本文档
│
├── （运行时自动生成）
├── old_versions/ # 旧版本 ZIP 自动迁移目录
├── zip_download_status.json # 下载状态记录（已完成、失败等）
├── zip_download_log.txt # 运行日志
├── .github_token # （可选）存放 GitHub Token 的文件
└── （下载的 ZIP 文件） # 格式：{owner}_{repo}@{short_sha}.zip
```
> **说明**：`GitHubZipDownloader.py` 与 `StartDownload.py` 功能完全相同，只是内部注释略有差异。您任选其一即可，推荐使用 `StartDownload.py`。

## 🔧 环境要求

- Python 3.6 或更高版本
- 需要安装 `requests` 库（可选 `tqdm` 以显示进度条）

安装依赖：

    pip install requests tqdm

## 🚀 快速开始

### 1. 准备 URL 列表文件

创建一个文本文件（例如 `repos.txt`），每行一个 GitHub 仓库的 URL，支持以下格式：

    https://github.com/owner/repo
    https://github.com/owner/repo.git
    https://github.com/owner/repo/

空行和以 `#` 开头的行会被忽略。

示例 `repos.txt`：

    # 这是注释行
    https://github.com/facebook/react
    https://github.com/vuejs/vue
    https://github.com/tensorflow/tensorflow

### 2. 运行下载工具

直接将 URL 列表文件**拖拽**到 `StartDownload.py` 程序图标上，或者在命令行中执行：

    python StartDownload.py /path/to/repos.txt

程序将：
- 解析每个 URL
- 获取仓库默认分支（`main` 或 `master`）及最新 commit SHA
- 生成 ZIP 文件名：`{owner}_{repo}@{short_sha}.zip`
- 若本地已存在该文件，跳过下载；否则下载并保存
- 若检测到同一仓库有更旧的版本文件（不同 SHA），将其移动到 `old_versions/` 目录
- 记录已完成和失败的 URL 到 `zip_download_status.json`

### 3. 运行完整性检查

在完成下载后（或定期维护时），运行 `CheckMissing.py` 检查是否有遗漏或多余文件。

**首先**，编辑 `CheckMissing.py` 开头的配置区域：

    INPUT_FILE = r"D:\0lib2\All.txt"      # 你的 GitHub URL 列表文件
    ZIP_ROOT = r"D:\0libZip"              # ZIP 文件存放目录
    OUTPUT_MISSING = r"D:\0lib2\miss.txt" # 缺失仓库输出文件
    OUTPUT_EXTRA = r"D:\0lib2\extra.txt"  # 多余 ZIP 文件输出文件
    VERBOSE = False                       # 是否打印详细匹配过程

然后执行：

    python CheckMissing.py

程序会：
- 读取 URL 列表，提取所有 `owner/repo` 前缀（转为小写）
- 扫描 ZIP 目录，提取所有 ZIP 文件的前缀（同样转为小写）
- 输出缺失的 URL 列表到 `miss.txt`
- 输出多余的 ZIP 文件列表到 `extra.txt`（以及无法解析命名的 ZIP 文件）

## ⚙️ 配置说明

### GitHub Token（可选，强烈推荐）

未认证时，GitHub API 对同一 IP 的请求限制为 **60 次/小时**。配置 Token 后可提升至 **5000 次/小时**。

**方法一：环境变量**

    # Windows (CMD)
    set GITHUB_TOKEN=your_token_here

    # Linux / macOS
    export GITHUB_TOKEN=your_token_here

**方法二：文件配置**
在下载工具同目录下创建 `.github_token` 文件，内容仅写入 Token 字符串（无空格、无换行）。

> 如何获取 Token？GitHub Settings → Developer settings → Personal access tokens → Generate new token（无需勾选任何权限，仅用于访问公共仓库）

### 可调整参数（在 `StartDownload.py` 中）

    self.max_retries = 3        # 最大重试次数
    self.retry_delay = 5        # 重试间隔（秒）
    self.download_timeout = 60  # 下载超时（秒）

## 📄 输出说明

### 下载的 ZIP 文件
- 命名规则：`{owner}_{repo}@{short_sha}.zip`  
  例如：`facebook_react@5f6c8e7.zip`
- 存放位置：与 `StartDownload.py` 同目录

### `old_versions/` 目录
当仓库更新后，旧版本的 ZIP 文件会自动移动到该目录。若文件名冲突，会自动添加时间戳，如 `facebook_react@3a4b5c6_20250101_120000.zip`。

### `zip_download_status.json`
记录每个 URL 的下载状态，格式示例：

    {
      "completed": {
        "https://github.com/facebook/react": {
          "zip_file": "facebook_react@5f6c8e7.zip",
          "commit_sha": "5f6c8e7a9b...",
          "branch": "main"
        }
      },
      "failed": {
        "https://github.com/owner/bad-repo": {
          "error": "invalid_url",
          "retry_count": 3,
          "final": true
        }
      },
      "last_updated": "2025-01-01T12:00:00"
    }

### `zip_download_log.txt`
详细的操作日志，包含时间戳、每个仓库的处理过程和错误信息。

### 检查工具输出
- `miss.txt`：缺失的仓库 URL（可直接作为下载列表再次运行）
- `extra.txt`：多余的 ZIP 文件名（可能是不在 URL 列表中的仓库或残留文件），以及无法解析命名的 ZIP 文件

## ⚠️ 注意事项

1. **大小写不敏感匹配**：检查工具忽略大小写，因此 `Owner/Repo` 可以匹配 `owner_repo.zip`。但下载工具生成的 ZIP 文件名中的 `owner` 和 `repo` 保持原始大小写（来自 URL 路径）。
2. **API 速率限制**：若未配置 Token 且仓库数量较多（>60），程序会自动等待速率限制重置。建议配置 Token。
3. **网络问题**：程序会重试超时、连接错误等临时性问题。对于 404、权限错误等永久性错误，会直接标记失败并跳过。
4. **手动放入 ZIP 文件**：如果手动放入符合命名规则（`{owner}_{repo}@{sha}.zip` 或 `{owner}_{repo}.zip`）的文件，下载工具会识别并跳过下载。但检查工具仍会按 URL 列表校验。
5. **中断恢复**：按 `Ctrl+C` 可安全中断下载，未完成的 ZIP 会被删除，状态文件保留已完成记录。
6. **仅支持公共仓库**：本工具设计用于下载公共仓库的 ZIP 包，私有仓库需要配置具有相应权限的 Token 并修改 API 请求头（代码已支持 Token，但私有仓库需额外验证）。

## 📝 常见问题

**Q：为什么下载的 ZIP 文件名包含一串短哈希？**  
A：文件名中的哈希是仓库最新 commit 的前 7 位，用于标识版本。这样当仓库更新后，新文件不会覆盖旧文件，而是并存（旧文件移至 `old_versions`）。

**Q：如何重新下载失败的仓库？**  
A：直接再次运行下载工具即可。程序会跳过已成功的仓库，只处理失败和未处理的 URL。

**Q：检查工具报告“无法解析前缀的 ZIP 文件”是什么意思？**  
A：表示该 ZIP 文件名不符合 `{owner}_{repo}[@{...}].zip` 的格式。检查工具无法判断它属于哪个仓库，需要手动处理（重命名或删除）。

**Q：是否支持 GitHub Enterprise 私有部署？**  
A：目前仅支持 `github.com`。如需支持 Enterprise，可修改代码中的域名判断逻辑。

## 📜 许可证

本项目采用 [MIT License](LICENSE)，可自由使用、修改和分发。

---

**Enjoy!** 如有问题，欢迎提交 Issue。