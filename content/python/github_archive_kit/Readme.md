# GitHub 归档工具集

本仓库汇集了两个实用的 GitHub 辅助工具，分别用于**星标仓库爬取与比较**、**批量 ZIP 下载与完整性检查**。适合需要备份、归档或批量处理 GitHub 仓库的场景。

## 📦 工具列表

### 1. GitHub Stars 爬虫 & URL 差异比较工具
- 获取指定用户的所有 Star 仓库 URL
- 比较两个 URL 列表的差异
- 自动处理 API 速率限制、支持 GitHub Token

👉 详细文档请查看：[stars_crawler/README.md](stars_crawler/README.md)

### 2. GitHub 批量 ZIP 下载与完整性检查工具
- 从文本文件批量下载仓库的 ZIP 压缩包（自动检测最新版本）
- 支持断点续传、旧版本自动迁移
- 双向检查缺失仓库和多余 ZIP 文件

👉 详细文档请查看：[zip_downloader/README.md](zip_downloader/README.md)

## 🚀 快速使用

1. 克隆本仓库
2. 进入对应工具的子文件夹，阅读其中的 README 了解详细配置和运行方法
3. 安装公共依赖：`pip install requests`（可选 `tqdm` 显示进度条）

## 📁 目录结构建议
```
github-archive-kit/
├── stars_crawler/ # 星标爬虫 + URL 比较
│ ├── stars_crawler.py
│ ├── url_diff.py
│ └── README.md
├── zip_downloader/ # 批量 ZIP 下载 + 完整性检查
│ ├── StartDownload.py
│ ├── CheckMissing.py
│ └── README.md
└── README.md # 本文件
```
> 你可以自由选择将两个工具放在同一个目录下运行，也可以分开放置。每个工具均独立运行，无需互相依赖。

## 📄 许可证

本项目采用 [MIT License](LICENSE)，可自由使用、修改和分发。
