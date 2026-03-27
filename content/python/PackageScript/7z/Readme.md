# 🗜️ 7Z压缩包处理工具集 (7Z Toolkit)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)  
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)  
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/)

> 四合一命令行工具｜**加密/解密/检损/格式转换**｜**批量处理**｜**进度可视化**｜**零基础秒上手**

---

## 🔒 工具1：7Z加密 (`7Z加密-Encrypt.py`)

### ✨ 三步加密
1. **改配置**（首次使用）  
   用记事本打开脚本 → 修改顶部两行：  
   ```python
   DEFAULT_TARGET_DIR = r"你的文件夹路径"  # 例：r"D:\待加密"
   DEFAULT_PASSWORD = "你的密码"           # 例："Secure2024"
   ```
2. **双击运行**  
   - 自动扫描文件夹内所有 `.7z` 文件  
   - 生成带密码的新文件：`原文件名_encrypted.7z`  
   - 进度条实时显示 ✅/❌ 状态
3. **完成**  
   处理结束后自动打开目标文件夹（Windows）

### ⚠️ 关键提示
- 原文件**永久保留**，仅生成加密副本
- 密码含特殊字符？建议用字母+数字组合
- 命令行高级用法：  
  `python "7Z加密-Encrypt.py" "D:\视频" "MyPass123"`

---

## 🔍 工具2：7Z检损 (`7Z检损-7ZDetection.py`)

### ✨ 两步检测
1. **改路径**  
   用记事本打开脚本 → 修改：  
   ```python
   TARGET_DIRECTORY = r"你的文件夹路径"  # 例：r"E:\备份"
   ```
2. **双击运行**  
   - 自动扫描所有 `.7z` 文件（含子文件夹）  
   - 终端输出清晰结果：  
     ✅ `所有7z文件均完整有效`  
     ❌ `发现 2 个损坏文件：xxx.7z, yyy.7z`

### ⚠️ 关键提示
- **仅支持无密码压缩包**（加密文件会误报损坏）
- 检测原理：调用 `7z t` 命令深度校验
- 损坏文件请重新下载或修复源文件

---

## 🔓 工具3：7Z解密 (`7Z解密-Decryption.py`)

### ✨ 三步解密
1. **改配置**  
   修改脚本顶部：  
   ```python
   DEFAULT_TARGET_DIR = r"加密文件所在文件夹"
   DEFAULT_PASSWORD = "原加密密码"  # ⚠️必须完全一致！
   ```
2. **双击运行**  
   - 输入正确密码 → 生成无密码新文件：`原文件名_decrypted.7z`  
   - 密码错误？终端提示 `[✕] 解密失败: xxx.7z - 子进程错误...`
3. **完成**  
   自动打开文件夹，原加密文件保留

### ⚠️ 关键提示
- 密码错误=解密失败（大小写/空格敏感）
- 原文件**不会被删除**，安全无忧
- 命令行用法：  
  `python "7Z解密-Decryption.py" "D:\加密包" "OriginalPass"`

---

## 🔄 工具4：7Z转RAR (`7Z转RAR-7ZConvert2RAR.py`)

### ✨ 两步转换
1. **改三处路径**  
   用记事本打开脚本 → 修改：  
   ```python
   TARGET_DIRECTORY = r"7z文件所在文件夹"
   SEVEN_ZIP_PATH = r"你的7z.exe路径"   # 例：r"C:\7-Zip\7z.exe"
   RAR_PATH = r"你的WinRAR.exe路径"    # 例：r"C:\Program Files\WinRAR\WinRAR.exe"
   ```
2. **双击运行**  
   - 自动转换所有 `.7z` → `.rar`  
   - 保留原目录结构，生成同名 `.rar` 文件  
   - 进度条实时反馈

### ⚠️ 关键提示
- **必须安装 WinRAR**（免费版即可）
- 源文件**保留不变**，仅新增 RAR 副本
- 加密的7z需先用【工具3】解密再转换

---

## 🌟 通用使用守则（必读！）

| 项目 | 操作指南 |
|------|----------|
| 📌 **首次使用** | 用记事本打开脚本 → 修改顶部 `用户配置区域` → 保存 |
| 🔑 **密码安全** | 脚本内密码仅为示例！处理敏感文件请改用强密码 |
| 🗂️ **文件安全** | 所有工具均**不删除原文件**，仅生成新文件 |
| 🌐 **中文支持** | 完美支持中文路径/文件名（无需改系统编码） |
| 🚫 **常见失败** | ①路径含空格未加引号 ②7z/WinRAR路径错误 ③密码错误 |
| 💡 **高效技巧** | 将脚本拖到桌面 → 修改配置后直接双击使用 |

> ✨ **新手推荐流程**：  
> 加密保护 → 检测完整性 → （需分享时）转RAR → （需解密时）移除密码  
> 每步独立操作，安全可控，零学习成本！