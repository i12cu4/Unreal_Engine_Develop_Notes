# 🗜️ 7Z Archive Processing Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)  
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)  
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/)

> All-in-one CLI suite | **Encrypt/Decrypt/Verify/Convert** | **Batch Processing** | **Visual Progress** | **Zero Learning Curve**

---

## 🔒 Tool 1: 7Z Encryptor (`7Z加密-Encrypt.py`)

### ✨ 3-Step Encryption
1. **Configure** (First-time only)  
   Open script in Notepad → Edit top section:  
   ```python
   DEFAULT_TARGET_DIR = r"your\archive\folder"  # Example: r"D:\Confidential"
   DEFAULT_PASSWORD = "YourSecurePass"          # Example: "ProjectX2024"
   ```
2. **Run**  
   Double-click script → Automatically processes all `.7z` files  
   → Generates password-protected copies: `original_encrypted.7z`  
   → Real-time progress bar with ✅/❌ status
3. **Done**  
   Target folder auto-opens after completion (Windows)

### ⚠️ Critical Notes
- Original files **remain untouched** (only new encrypted copies created)
- For special characters in passwords: Prefer alphanumeric combinations
- CLI usage:  
  `python "7Z加密-Encrypt.py" "D:\Videos" "MyPass123"`

---

## 🔍 Tool 2: 7Z Integrity Checker (`7Z检损-7ZDetection.py`)

### ✨ 2-Step Verification
1. **Configure**  
   Edit script:  
   ```python
   TARGET_DIRECTORY = r"your\archive\folder"  # Example: r"E:\Backups"
   ```
2. **Run**  
   Double-click → Scans all `.7z` files (including subfolders)  
   → Clear terminal output:  
     ✅ `All 7z files are valid and intact`  
     ❌ `Found 2 corrupted files: xxx.7z, yyy.7z`

### ⚠️ Critical Notes
- **Password-free archives ONLY** (encrypted files will falsely report as corrupted)
- Verification method: Uses `7z t` for bit-level integrity check
- Corrupted files require re-downloading or source repair

---

## 🔓 Tool 3: 7Z Decryptor (`7Z解密-Decryption.py`)

### ✨ 3-Step Decryption
1. **Configure**  
   Edit script:  
   ```python
   DEFAULT_TARGET_DIR = r"folder\with\encrypted\archives"
   DEFAULT_PASSWORD = "OriginalEncryptionPassword"  # ⚠️ Must match EXACTLY!
   ```
2. **Run**  
   Correct password → Generates unprotected copies: `original_decrypted.7z`  
   Wrong password → `[✕] Decryption failed: xxx.7z - Subprocess error...`
3. **Done**  
   Folder auto-opens; original encrypted files preserved

### ⚠️ Critical Notes
- Password is **case-sensitive** (spaces matter!)
- Original files **never deleted** – completely safe
- CLI usage:  
  `python "7Z解密-Decryption.py" "D:\Encrypted" "OriginalPass"`

---

## 🔄 Tool 4: 7Z to RAR Converter (`7Z转RAR-7ZConvert2RAR.py`)

### ✨ 2-Step Conversion
1. **Configure THREE paths**  
   Edit script:  
   ```python
   TARGET_DIRECTORY = r"folder\with\7z\files"
   SEVEN_ZIP_PATH = r"your\7z.exe\path"    # Example: r"C:\Program Files\7-Zip\7z.exe"
   RAR_PATH = r"your\WinRAR.exe\path"      # Example: r"C:\Program Files\WinRAR\WinRAR.exe"
   ```
2. **Run**  
   Double-click → Converts all `.7z` → `.rar`  
   → Preserves folder structure  
   → Generates same-name `.rar` files with progress tracking

### ⚠️ Critical Notes
- **WinRAR must be installed** (free evaluation version works)
- Source files **remain unchanged** – only new RAR copies created
- Encrypted 7z files must be decrypted first (use Tool 3)

---

## 🌟 Universal Quick Start Guide (MUST READ!)

| Task                  | Action                                                                         |
| --------------------- | ------------------------------------------------------------------------------ |
| 📌 **First Launch**    | Open script in Notepad → Edit `User Configuration Section` at top → Save       |
| 🔑 **Password Safety** | Default passwords are EXAMPLES ONLY! Use strong passwords for sensitive data   |
| 🗂️ **File Safety**     | **NO tool deletes originals** – all operations create new files only           |
| 🌐 **Unicode Support** | Full Chinese path/filename support (no system encoding changes needed)         |
| 🚫 **Common Failures** | ① Paths with spaces not quoted ② Incorrect 7z/WinRAR paths ③ Password mismatch |
| 💡 **Pro Tip**         | Pin scripts to desktop → Configure once → Double-click for instant use         |

> ✨ **Recommended Workflow for Beginners**:  
> Encrypt → Verify Integrity → (If sharing) Convert to RAR → (If needed) Decrypt  
> Each step is independent, safe, and requires zero prior knowledge!  
> **You're ready in 60 seconds.**