# 🗜️ ZIP Archive Processing Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)  
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)  
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/)

> Professional 3-in-1 suite | **Re-encrypt/Decrypt/Convert** | **AES-256 Security** | **Batch Processing** | **Zero Learning Curve**

---

## 🔒 Tool 1: ZIP Re-encryptor (`ZIP加密-Encrypt.py`)

### ✨ Core Purpose  
Re-encrypt **password-protected ZIP files** into modern AES-256 format (same password, enhanced security)

### 📌 3-Step Operation
1. **Install Dependency** (First-time only)  
   ```bash
   pip install pyzipper
   ```
2. **Configure Password**  
   Open script in Notepad → Edit:  
   ```python
   DEFAULT_PASSWORD = "CurrentZIPPassword"  # ⚠️ MUST match existing ZIP password exactly!
   ```
3. **Run**  
   Double-click → Generates: `original_encrypted.zip`  
   → Terminal shows verification command example

### ⚠️ Critical Notes
- **Only processes password-protected ZIPs** (password-free ZIPs will fail)
- Original files **remain untouched** – only creates AES-256 encrypted copies
- New files require **same password** to extract (see terminal verification command)
- CLI usage:  
  `python "ZIP加密-Encrypt.py" -d "D:\Archives" -p "MyPass"`

---

## 🔓 Tool 2: ZIP Decryptor (`ZIP解密-Decryption.py`)

### ✨ Core Purpose  
Completely remove password protection from ZIP files → generate fully password-free archives

### 📌 3-Step Operation
1. **Install Dependency** (First-time only)  
   ```bash
   pip install pyzipper
   ```
2. **Configure Password**  
   Edit script:  
   ```python
   PASSWORD = "CurrentZIPPassword"  # ⚠️ Must be 100% accurate!
   OUTPUT_SUFFIX = "_nopassword"    # Customizable output suffix
   ```
3. **Run**  
   Double-click → Generates password-free files: `original_nopassword.zip`  
   → Real-time progress bar with ✅/❌ status

### ⚠️ Critical Notes
- Wrong password = `[✕] Processing failed: Password error`
- Original encrypted files **never deleted** – completely safe
- New files extract instantly (no password required)
- Auto-detects corrupted archives ("Damaged ZIP file" warning)

---

## 🔄 Tool 3: ZIP to RAR Converter (`ZIP转RAR-ZIPConvert2RAR.py`)

### ✨ Core Purpose  
Convert **password-free ZIP files** to RAR format (preserves folder structure)

### 📌 2-Step Operation
1. **Configure Paths**  
   Edit script:  
   ```python
   DEFAULT_TARGET_DIR = r"folder\with\zip\files"
   WINRAR_PATH = r"your\WinRAR.exe\path"  # Example: r"C:\Program Files\WinRAR\WinRAR.exe"
   ```
2. **Run**  
   Double-click → Generates same-name `.rar` files  
   → Progress tracking → Auto-opens folder after completion

### ⚠️ Critical Notes
- **WinRAR must be installed** (free evaluation version works)
- **Password-free ZIPs ONLY** (encrypted ZIPs must be decrypted first with Tool 2)
- Original ZIP files **remain unchanged** – only creates RAR copies
- CLI usage:  
  `python "ZIP转RAR-ZIPConvert2RAR.py" "D:\Files"`

---

## 🌟 Universal Quick Start Guide (MUST READ!)

| Task                       | Action                                                                                                                                    |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 📦 **Dependencies**         | Tools 1/2: `pip install pyzipper`<br>Tool 3: Install WinRAR (official website)                                                            |
| 🔑 **Password Rules**       | Tool 1: Password = current ZIP password (for decryption + re-encryption)<br>Tool 2: Password = current ZIP password (for decryption)      |
| 🔄 **Recommended Workflow** | Password-protected ZIP → [Tool 2: Decrypt] → [Tool 3: Convert to RAR]<br>Need stronger encryption? → [Tool 1: Re-encrypt] (same password) |
| 🗂️ **File Safety**          | **NO tool deletes originals** – all operations create new files only                                                                      |
| 🌐 **Unicode Support**      | Full Chinese path/filename support (no system encoding changes needed)                                                                    |
| 💡 **Pro Tip**              | Pin scripts to desktop → Configure once → Double-click for instant use                                                                    |

> ✨ **Beginner's 3-Step Path**:  
> 1️⃣ Password-protected ZIP? → Use **Tool 2** to remove password  
> 2️⃣ Need RAR format? → Use **Tool 3** to convert  
> 3️⃣ Need stronger encryption? → Use **Tool 1** to re-encrypt (same password)  
> **Each step is independent, safe, and ready in 10 seconds!**  
> *You're in control – no expertise required.*