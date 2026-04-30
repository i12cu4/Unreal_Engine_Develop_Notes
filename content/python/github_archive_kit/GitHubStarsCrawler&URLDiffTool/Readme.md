# GitHub Stars 爬虫 & URL 差异比较工具

本仓库提供两个小工具：
- **GitHub Stars 爬虫**：获取指定 GitHub 用户所有 Star 过的仓库 URL 列表。
- **URL 差异比较工具**：对比两个文本文件中的 URL，找出第一个文件中有而第二个文件中没有的 URL。

适用于备份自己的 Star 列表、对比不同来源的仓库列表等场景。

## ✨ 功能特点

### ⭐ GitHub Stars 爬虫（`stars_crawler.py`）
- ✅ 通过 GitHub API 获取用户所有 Star 仓库（每页 100 条）
- ✅ 自动处理 API 速率限制（403 错误），智能等待至限制重置
- ✅ 支持自定义最大页数、重试次数、重试等待时间
- ✅ 自动去重，避免重复 URL
- ✅ 生成两个输出文件：完整 URL 列表（`.txt`）和统计摘要（`_summary.txt`）
- ✅ 友好的进度提示，显示当前页、重试状态、预计等待时间

### 🔍 URL 差异比较工具（`url_diff.py`）
- ✅ 读取两个文本文件（每行一个 URL）
- ✅ 计算 **A 中有但 B 中没有** 的 URL 集合
- ✅ 自动去重（基于集合运算）
- ✅ 可选的输出文件保存结果
- ✅ 显示统计信息：A 总数、B 总数、独有数量

## 📁 文件结构
```
├── stars_crawler.py # GitHub Stars 爬虫主程序
├── url_diff.py # URL 差异比较工具
├── README.md # 本文档
│
├── （运行时生成）
├── github_stars_<用户名>all_api.txt # 爬取的完整 URL 列表
├── github_stars<用户名>_all_api_summary.txt # 统计摘要
└── （可选输出文件，由 diff 工具生成）
```

## 🔧 环境要求

- Python 3.6 或更高版本
- 需要安装 `requests` 库

安装依赖：

    pip install requests

## 🚀 快速开始

### 1. 配置并运行 Stars 爬虫

编辑 `stars_crawler.py` 开头的配置项：

    USERNAME = "i12cu4"               # 要爬取的用户名
    OUTPUT_FILE = f"github_stars_{USERNAME}_all_api.txt"  # 输出文件名
    MAX_PAGES = 10                    # 最大爬取页数（每页 100 个）
    MAX_RETRIES = 500                 # 遇到错误时的最大重试次数
    RETRY_DELAY = 5                   # 普通重试等待（秒）
    RATE_LIMIT_WAIT = 3600            # 被限速时等待时间（秒）

然后运行：

    python stars_crawler.py

程序会：
- 依次请求 GitHub API 的每一页
- 如果遇到 403 速率限制，自动根据 `X-RateLimit-Reset` 头部等待足够时间
- 每页请求后自动休眠 0.5 秒以降低频率
- 最后保存所有 Star 仓库 URL 到文件，并生成摘要

**建议配置 GitHub 个人访问令牌（PAT）**：  
在 `headers` 中添加 `Authorization: token YOUR_TOKEN` 可将 API 限额从 60 次/小时提升至 5000 次/小时。具体方法见下文“配置说明”。

### 2. 使用 URL 差异比较工具

编辑 `url_diff.py` 底部的示例部分：

    file_a = r"D:\path\to\fileA.txt"   # A 文件路径
    file_b = r"D:\path\to\fileB.txt"   # B 文件路径
    output_file = "diff_result.txt"    # 输出文件（设为 None 则不保存）

运行：

    python url_diff.py

程序会输出：

    A文件总共有 xxx 个网址
    B文件总共有 xxx 个网址
    A文件中独有的网址有 xxx 个

    然后列出所有独有的 URL（如果存在）。

## ⚙️ 配置说明

### GitHub 个人访问令牌（强烈推荐）

未认证时，GitHub API 对同一 IP 的限制为 **60 次/小时**。对于 Star 数量较多的用户（> 600），很容易触发限制。配置 Token 后限额为 **5000 次/小时**。

**方法**：在 `stars_crawler.py` 中创建 Token 并添加到 headers：

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token ghp_xxxxxxxxxxxxx'   # 替换为你的实际 Token
    }

如何获取 Token：  
GitHub Settings → Developer settings → Personal access tokens → Generate new token（无需勾选任何权限，仅用于公共 API）。

### 爬虫参数调整

- `MAX_PAGES`：如果你 star 的仓库少于 100 个，设为 1 即可；如果很多，可适当调大。API 最多返回 1000 条（10 页），但程序不会自动超过 `MAX_PAGES`。
- `MAX_RETRIES`：遇到网络错误或非 200/403 状态码时的重试次数。建议保持较大值（如 500），避免因临时故障中断。
- `RATE_LIMIT_WAIT`：当收到 403 限速响应时的默认等待时间（秒）。程序会优先根据 `X-RateLimit-Reset` 头精确等待，仅当该头缺失时使用此值。

### 差异比较工具参数

- 两个输入文件应为纯文本，每行一个 URL（支持任意 URL 格式，不限于 GitHub）。
- `output_file`：如果提供，将结果写入该文件；如果为 `None` 或空字符串，则不保存。

## 📄 输出说明

### Stars 爬虫输出

1. **主文件**：`github_stars_<用户名>_all_api.txt`  
   每行一个 Star 仓库的完整 URL，已排序。  
   示例：

        https://github.com/facebook/react
        https://github.com/vuejs/vue

2. **摘要文件**：`github_stars_<用户名>_all_api_summary.txt`  
   包含爬取时间、总数量、前 10 个 URL 等信息。

### 差异比较工具输出

- 如果 `output_file` 指定了路径，则输出文件包含 A 中独有的 URL（每行一个）。
- 无论是否保存文件，程序都会在控制台打印统计信息和列表（如果独有数量较少）。

## ⚠️ 注意事项

1. **API 速率限制**：未使用 Token 时，爬取超过 60 个 Star 的仓库几乎必然触发限速。程序会等待直到限制重置，但等待时间可能长达一小时。**强烈建议配置 Token**。
2. **爬虫的页数限制**：GitHub API 默认每页最多 100 条，最多返回 1000 条（10 页）。如果你 Star 的仓库超过 1000 个，需要修改分页逻辑（但极为罕见）。
3. **差异比较工具的编码**：默认使用 UTF-8 编码读取和写入。如果文件为其他编码，请修改 `open` 中的 `encoding` 参数。
4. **网络稳定性**：爬虫在网络错误时会自动重试，但需确保重试次数足够多（`MAX_RETRIES` 较大）。

## 📝 常见问题

**Q：爬虫运行到一半卡住了，显示“被 GitHub API 限制访问”怎么办？**  
A：这是正常现象。程序会等待限制重置（通常一小时），然后自动继续。如果想加快速度，请配置个人访问令牌。

**Q：爬虫保存的 URL 不全，只有一部分？**  
A：检查 `MAX_PAGES` 是否设置过小。如果 Star 数量超过 1000，API 只能返回前 1000 条（GitHub 限制）。此时可以考虑使用更高级的方法（如 GraphQL）或分时段多次爬取。

**Q：差异比较工具中 A 和 B 文件顺序重要吗？**  
A：重要。该工具只找出 **A 中有而 B 中没有** 的 URL。如果想找 B 中有而 A 中没有，只需交换两个参数即可。

**Q：能否比较非 URL 的普通文本？**  
A：可以，只要每行是需要比较的字符串（不一定是 URL）。工具仅做集合差集运算。

## 📜 许可证

本项目采用 [MIT License](LICENSE)，可自由使用、修改和分发。

---

**Enjoy!** 如有问题，欢迎提交 Issue。