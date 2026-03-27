# 🗜️ ZIP压缩包处理工具集 (ZIP Toolkit)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)  
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)  
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/)

> 三合一专业工具｜**重加密/解密/转RAR**｜**AES-256安全加密**｜**批量处理**｜**零基础秒上手**

---

## 🔒 工具1：ZIP重加密 (`ZIP加密-Encrypt.py`)

### ✨ 核心用途
将**已有密码的ZIP文件**重新加密为AES-256标准格式（密码不变，提升安全性）

### 📌 三步操作
1. **安装依赖**（首次使用）  
   ```bash
   pip install pyzipper
   ```
2. **配置密码**  
   用记事本打开脚本 → 修改：  
   ```python
   DEFAULT_PASSWORD = "你的原始密码"  # ⚠️必须与ZIP当前密码完全一致！
   ```
3. **运行**  
   双击脚本 → 生成新文件：`原文件名_encrypted.zip`  
   → 终端显示验证命令示例

### ⚠️ 关键提示
- **仅处理已加密ZIP**（无密码ZIP会解压失败）
- 原文件**永久保留**，仅生成AES-256加密新副本
- 生成文件需用**相同密码**解压（验证命令见终端输出）
- 命令行用法：  
  `python "ZIP加密-Encrypt.py" -d "D:\Archives" -p "MyPass"`

---

## 🔓 工具2：ZIP解密 (`ZIP解密-Decryption.py`)

### ✨ 核心用途
彻底移除ZIP文件密码保护，生成完全无密码的新文件

### 📌 三步操作
1. **安装依赖**（首次使用）  
   ```bash
   pip install pyzipper
   ```
2. **配置密码**  
   修改脚本：  
   ```python
   PASSWORD = "ZIP当前密码"  # ⚠️必须100%准确！
   OUTPUT_SUFFIX = "_nopassword"  # 新文件后缀（可自定义）
   ```
3. **运行**  
   双击脚本 → 生成无密码文件：`原文件名_nopassword.zip`  
   → 进度条实时显示 ✅/❌ 状态

### ⚠️ 关键提示
- 密码错误 = `[✕] 处理失败: 密码错误`
- 原加密文件**不会被删除**，安全无忧
- 新文件可直接双击解压（无需密码）
- 支持损坏文件检测（自动标记"损坏的ZIP文件"）

---

## 🔄 工具3：ZIP转RAR (`ZIP转RAR-ZIPConvert2RAR.py`)

### ✨ 核心用途
将**无密码ZIP文件**转换为RAR格式（保留目录结构）

### 📌 两步操作
1. **配置路径**  
   修改脚本：  
   ```python
   DEFAULT_TARGET_DIR = r"ZIP文件所在文件夹"
   WINRAR_PATH = r"你的WinRAR.exe路径"  # 例：r"C:\Program Files\WinRAR\WinRAR.exe"
   ```
2. **运行**  
   双击脚本 → 生成同名 `.rar` 文件  
   → 进度条实时反馈，完成后自动打开文件夹

### ⚠️ 关键提示
- **必须安装 WinRAR**（免费版即可）
- **仅支持无密码ZIP**（加密ZIP需先用【工具2】解密）
- 原ZIP文件**保留不变**，仅新增RAR副本
- 命令行用法：  
  `python "ZIP转RAR-ZIPConvert2RAR.py" "D:\Files"`

---

## 🌟 通用使用守则（必读！）

| 项目             | 操作指南                                                                          |
| ---------------- | --------------------------------------------------------------------------------- |
| 📦 **依赖安装**   | 工具1/2：`pip install pyzipper`<br>工具3：安装WinRAR（官网下载）                  |
| 🔑 **密码规则**   | 工具1：密码=当前ZIP密码（用于解压+重加密）<br>工具2：密码=当前ZIP密码（用于解密） |
| 🔄 **工作流推荐** | 有密码ZIP →【工具2解密】→【工具3转RAR】<br>需提升加密强度 →【工具1重加密】        |
| 🗂️ **文件安全**   | **所有工具绝不删除原文件**，仅生成新文件                                          |
| 🌐 **中文支持**   | 完美支持中文路径/文件名（无需改系统设置）                                         |
| 💡 **高效技巧**   | 将脚本拖到桌面 → 配置一次 → 双击即用                                              |

> ✨ **新手三步走**：  
> 1️⃣ 有密码ZIP？→ 用【工具2】移除密码  
> 2️⃣ 需转RAR？→ 用【工具3】转换  
> 3️⃣ 需更强加密？→ 用【工具1】重加密（密码不变）  
> **每步独立安全，10秒上手！**