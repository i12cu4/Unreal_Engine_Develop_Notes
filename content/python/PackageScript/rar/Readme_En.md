# 📦 RAR Toolkit (7-Script Professional Edition) User Guide  
## 💡 Structure Analysis · Encryption/Decryption · Quality Inspection · Smart Compression  

---

## 📂 Project Structure  
RAR Toolkit (Pro Edition)/  
├── 🌳 RAR导出层级-OutputFileDir.py        ← Export RAR internal tree structure (Chinese-friendly)  
├── 🔒 RAR加密-Encrypt.py                  ← Batch encrypt RARs (preserves originals)  
├── 🔓 RAR解密-Decryption.py               ← Batch decrypt RARs (generates password-free copies)  
├── 🔍 RAR检二压-RARSecondaryCompression.py ← Detect nested compressed archives inside RARs  
├── 🛠️ RAR检损-RARDetection.py             ← Comprehensive RAR integrity verification  
├── 📦 RAR压缩-Package.py                  ← Smart folder compression (excludes redundant items)  
└── 🔄 RAR压中压.py                        ← Detect + move RARs containing nested archives  

---

## 🌳 Script 1: RAR导出层级-OutputFileDir.py (Structure Visualization)  
### Function  
Export RAR internal file structure as tree-formatted text:  
✅ Multi-encoding smart decoding (perfect Chinese path support)  
✅ Auto-generates same-name .txt file (overwrites old)  
✅ Empty archive detection + file count statistics  
✅ Real-time progress feedback  
🎯 Use cases: Resource package structure review, delivery documentation, teaching demos  

### Configuration  
| Setting          | Description                     | Example                        |
| ---------------- | ------------------------------- | ------------------------------ |
| Target Directory | Folder containing RAR files     | E:\Download                    |
| WinRAR Path      | Rar.exe path (**note: NO "s"**) | C:\Program File\WinRAR\Rar.exe |

⚠️ Note: Existing .txt files will be overwritten (backup important reports first)  

---

## 🔒 Script 2: RAR加密-Encrypt.py (Security Hardening)  
### Function  
Add password protection to RARs, generating encrypted copies:  
✅ Original files preserved (new files with "_encrypted" suffix)  
✅ Dual encryption: filenames + content (-hp parameter)  
✅ Temporary extraction auto-cleanup (no residue risk)  
✅ Detailed logging (includes DEBUG-level diagnostics)  
🎯 Use cases: Sensitive resource distribution, client delivery encryption, privacy protection  

### Configuration  
| Setting          | Description                                              | Example                                 |
| ---------------- | -------------------------------------------------------- | --------------------------------------- |
| Target Directory | Directory with RARs to encrypt (recursive)               | C:\Users\chru\Desktop\UE-VRGK-v2-master |
| Password         | **MUST BE CHANGED!** (Default "1234" is highly insecure) | 1234 → **SET STRONG PASSWORD**          |
| Output Suffix    | Encrypted file identifier                                | _encrypted                              |
| WinRAR Path      | WinRar.exe path (**note: NO "s"**)                       | C:\Program File\WinRAR\WinRar.exe       |

⚠️ **SECURITY WARNING**: Default password is "1234"! **ALWAYS change to strong password before use**  

---

## 🔓 Script 3: RAR解密-Decryption.py (Secure Decryption)  
### Function  
Decrypt password-protected RARs, generating password-free copies:  
✅ Original encrypted files preserved (new files with "_decrypted" suffix)  
✅ Password must exactly match encryption password  
✅ Temporary extraction auto-cleanup  
✅ Detailed processing logs  
🎯 Use cases: Decrypting received resources, password rotation, internal distribution  

### Configuration  
| Setting          | Description                                | Example                                 |
| ---------------- | ------------------------------------------ | --------------------------------------- |
| Target Directory | Directory with encrypted RARs (recursive)  | C:\Users\chru\Desktop\UE-VRGK-v2-master |
| Password         | **Must exactly match encryption password** | 1234                                    |
| Output Suffix    | Decrypted file identifier                  | _decrypted                              |
| WinRAR Path      | WinRar.exe path (**note: NO "s"**)         | C:\Program File\WinRAR\WinRar.exe       |

⚠️ Note: Incorrect password causes failure; ensure sufficient disk space  

---

## 🔍 Script 4: RAR检二压-RARSecondaryCompression.py (Nested Archive Detection)  
### Function  
Scan RAR contents for embedded compressed archives:  
✅ Precise detection of .zip/.7z/.rar nested files  
✅ Grouped statistics by archive type (clear quantity display)  
✅ Full Chinese filename support  
✅ Invalid files skipped with warning prompts  
🎯 Use cases: Resource package QA, anti-malware screening, pre-delivery checks  

### Configuration  
| Setting          | Description                     | Example                        |
| ---------------- | ------------------------------- | ------------------------------ |
| Target Directory | Directory to scan (recursive)   | E:\Download                    |
| WinRAR Path      | rar.exe path (**note: NO "s"**) | C:\Program File\WinRAR\rar.exe |

---

## 🛠️ Script 5: RAR检损-RARDetection.py (Integrity Verification)  
### Function  
Comprehensive RAR file integrity check:  
✅ Deep per-file verification (not just header check)  
✅ Real-time status feedback ([OK]/[Damaged] indicators)  
✅ Damaged file list summary output  
✅ Multi-path tolerance (auto-matches WinRAR installation)  
🎯 Use cases: Download verification, archive health checks, final pre-delivery inspection  

### Configuration  
| Setting          | Description                        | Example                           |
| ---------------- | ---------------------------------- | --------------------------------- |
| Target Directory | Directory to verify (recursive)    | C:\Users\chru\Downloads\agw       |
| WinRAR Path      | WinRar.exe path (**note: NO "s"**) | C:\Program File\WinRAR\WinRar.exe |

⚠️ Note: Large file verification takes time (please be patient); checks only, no repair  

---

## 📦 Script 6: RAR压缩-Package.py (Smart Packaging)  
### Function  
Batch compress folders with automatic redundancy exclusion:  
✅ **Drag-and-drop operation**: Drag folders directly onto script  
✅ Smart exclusion: Auto-skips .vs/.svn/Binaries and other redundant directories  
✅ Filename sanitization: Auto-handles special characters (brackets/spaces)  
✅ Current directory fallback: Compresses current dir if no drag-drop  
🎯 Use cases: Resource packaging delivery, project archiving, daily backups  

### Configuration  
| Setting      | Description                                      | Example                        |
| ------------ | ------------------------------------------------ | ------------------------------ |
| Exclude List | Auto-skipped files/folders (wildcards supported) | .vs, Binaries, *.rar           |
| WinRAR Path  | Rar.exe path (**note: NO "s"**)                  | C:\Program File\WinRAR\Rar.exe |

⚠️ Note: Large folder compression takes time; ensure sufficient disk space  

---

## 🔄 Script 7: RAR压中压.py (Detection + Relocation)  
### Function  
Detect RARs containing other archives + optional relocation:  
✅ **Drag-and-drop operation**: Supports files/folders batch detection  
✅ Smart identification: Precise detection of .zip/.7z/.rar nesting  
✅ One-click relocation: Detected files auto-moved to target directory  
✅ Existence check: Skips if same-name file exists in target  
🎯 Use cases: Resource library cleanup, nested archive processing, automation pipelines  

### Configuration  
| Setting          | Description                                             | Example                        |
| ---------------- | ------------------------------------------------------- | ------------------------------ |
| WinRAR Path      | Rar.exe path (**note: NO "s"**)                         | C:\Program File\WinRAR\Rar.exe |
| Target Move Path | Destination for detected files (leave empty to disable) | D:\NestedCompressedArchives    |

⚠️ Note: Verify target path validity before moving; same-name files skipped  

---

## ⚠️ Universal Critical Reminders (MUST READ!)  
| Issue                             | Solution                                                                                                |
| --------------------------------- | ------------------------------------------------------------------------------------------------------- |
| "rar.exe not found" in any script | Script uses "Program File" (**NO "s"**) → Modify to match actual install path (usually "Program Files") |
| Chinese garbled text              | Set system locale to Chinese (Control Panel → Region → Chinese)                                         |
| Script 2/3 password issues        | Script 2 password **MUST be changed**; Script 3 password must exactly match encryption password         |
| Drag-and-drop fails               | Ensure dragging folders directly onto .py file (not shortcut)                                           |
| First-time use                    | Always test with sample files before batch processing                                                   |

---

## 💡 Efficient Workflow Combination  
✨ **End-to-End Resource Package Delivery**:  
1️⃣ Use 【Script 6】to compress project (auto-excludes redundancies)  
2️⃣ Use 【Script 5】for integrity check → Ensure file completeness  
3️⃣ Use 【Script 4/7】to detect nested archives → Clean embedded compressions  
4️⃣ Use 【Script 1】to export structure → Generate documentation for delivery  
5️⃣ Use 【Script 2】to encrypt → Secure sensitive resource distribution  
6️⃣ Recipient uses 【Script 3】to decrypt → Obtain password-free resources  

✨ **Security Protocol**:  
✅ Script 2 password **MUST be changed** (default "1234" is critically insecure!)  
✅ Backup originals before critical operations (10 seconds saves hours!)  
✅ Path reminder: All scripts use "Program File" (**NO "s"**) → Adjust configuration to match your actual WinRAR installation path!  
