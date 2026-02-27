# 🎬 视频快剪辑 (Video Quick Editing)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/)

> 一款专为高效视频处理设计的命令行工具｜**流拷贝零参数修改**｜**智能文件名处理**｜**无残留临时文件**

---

## ✨ 核心特性

| 特性               | 说明                                                           |
| ------------------ | -------------------------------------------------------------- |
| 🔒 **参数零修改**   | 全程 `-c copy` 流拷贝，100% 保留原始帧率/分辨率/编码/音频参数  |
| ⏱️ **精准时间裁剪** | 严格按 `起始→结束` 时间点裁剪（如 `4:30→4:41` = 精确11秒内容） |
| 🧠 **智能文件名**   | 输入视频名可省略扩展名（输入 `Video` 自动匹配 `Video.mp4`）    |
| 📁 **规范命名**     | 导出文件自动添加源文件前缀：`源文件名_标识.扩展名`             |
| 🧹 **无残留清理**   | 临时文件/concat文件自动清理，目录始终保持整洁                  |
| 🔄 **高效循环**     | 处理完自动进入下一轮，无需重复确认                             |
| 🌐 **中文友好**     | 完美支持中文路径、中文文件名、中文提示                         |
| 🛡️ **安全防护**     | 覆盖确认、非法字符拦截、异常自动清理                           |

---

## 📋 环境要求

- **操作系统**: Windows 7/10/11
- **Python**: 3.6 或更高版本
- **FFmpeg**: 
  - 默认路径：`C:\Program File\ffmpeg\bin\ffmpeg.exe`  
  - [FFmpeg 官网下载](https://ffmpeg.org/download.html)

> 💡 **重要提示**：若您的 FFmpeg 安装在其他路径，请修改 `main.py` 第 7 行的 `FFMPEG_PATH` 变量
