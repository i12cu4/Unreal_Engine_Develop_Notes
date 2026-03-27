# 📦 RAR Toolkit: 4-in-1 User Guide  
## 💡 Precision Tools · Zero-Config Setup · Workflow Optimized  

---

## 📂 Project Structure  
RAR Toolkit/  
├── 🌟 ImageSeed.py                          ← Create hybrid image (PNG cover + hidden RAR)  
├── 🧹 RAR_CheckFileExistence-RarFileExistenceDetection.py ← Smart RAR cleanup  
├── 🖼️ RAR_ExtractImages-RarUnzipsPicture.py ← Batch extract cover images from RARs  
└── 🏷️ RAR_PrefixRename-RarReanme(Overwrite).py ← Auto-rename RARs by content  

---

## 🌟 Script 1: ImageSeed.py (Create Hybrid Image)  
### Function  
Seamlessly merge PNG + RAR into one file:  
✅ Open with image viewer → Shows original PNG  
✅ Open with WinRAR/7-Zip → Extracts hidden RAR contents  
✅ Rename to .rar → Same extraction result  
🎯 Use cases: Stealth sharing, fun projects, backup camouflage  

### Steps  
1️⃣ Prepare files:  
   - Cover image (PNG format, e.g., 1.png)  
   - Target RAR to hide (e.g., 2.rar)  
2️⃣ Edit script (Notepad):  
   - source_png_path → Full path to cover image  
   - source_rar_path → Full path to RAR file  
   - destination_png_path → Save path for hybrid image  
3️⃣ Double-click to run → Generates new PNG (e.g., 3.png)  
4️⃣ Verify:  
   - Image viewer: Displays cover normally  
   - WinRAR: Extracts original RAR contents  

⚠️ Notes:  
- PNG only (JPG merging often corrupts file)  
- Output size = PNG size + RAR size  
- Paths with Chinese/spaces fully supported  

---

## 🧹 Script 2: RAR_CheckFileExistence-RarFileExistenceDetection.py (Smart Cleanup)  
### Function  
Scan and safely remove redundant items from RARs (build caches, ads, etc.):  
✅ Custom delete patterns (files/folders)  
✅ Safe replacement (original preserved on failure)  
✅ Real-time console + detailed CSV report  
✅ Visual progress bar  
🎯 Use cases: Pre-delivery cleanup, batch optimization, audit trails  

### Configuration  
| Setting          | Description                              | Example                                     |
| ---------------- | ---------------------------------------- | ------------------------------------------- |
| WinRAR path      | Main executable (note: NO "s" in script) | C:\Program File\WinRAR\WinRAR.exe           |
| RAR CLI path     | Rar.exe path (note: NO "s")              | C:\Program File\WinRAR\Rar.exe              |
| Target directory | Folder containing RARs                   | G:\agw                                      |
| Delete patterns  | Items to remove (ads/build files)        | Saved, Intermediate, Build, .url/.txt files |
| Report type      | console/csv/both                         | both                                        |
| CSV save dir     | Report output location                   | Same as target                              |

### Steps  
1️⃣ Edit script → Update 【User Configuration Section】  
2️⃣ Double-click → Auto-scans and cleans matching items  
3️⃣ Review results:  
   - Console: Real-time [Success]/[Skipped]/[Failed] status  
   - CSV: Full details (paths, deleted items, errors)  

⚠️ Notes:  
- Script uses "Program File" (NO "s") → Modify to match your install path  
- Backup critical RARs before first run  
- Open CSV in Excel: Select encoding "UTF-8" (WPS opens directly)  

---

## 🖼️ Script 3: RAR_ExtractImages-RarUnzipsPicture.py (Batch Cover Extraction)  
### Function  
Auto-extract images from RARs to same directory with duplicate protection:  
✅ Prioritizes root images → falls back to subfolders  
✅ Skips if same-name image exists  
✅ Live progress tracking  
✅ Auto-cleanup temp files  
🎯 Use cases: Thumbnail generation, preview libraries, asset archiving  

### Configuration  
| Setting     | Description                 | Example                        |
| ----------- | --------------------------- | ------------------------------ |
| Target path | Folder containing RARs      | C:\Users\chru\Desktop\Task     |
| WinRAR path | Rar.exe path (note: NO "s") | C:\Program File\WinRAR\Rar.exe |

### Steps  
1️⃣ Place RARs in target folder  
2️⃣ Edit script paths  
3️⃣ Double-click → Generates .png/.jpg files named after RARs  
4️⃣ Check results:  
   - Success: New images appear in folder  
   - Skipped: "Image exists, skipping..." message  
   - Failed: Clear error reason shown  

⚠️ Notes:  
- Extracts first matching image only (.png/.jpg)  
- Chinese paths: Set system locale to Chinese  
- Temp files auto-deleted (no manual cleanup)  

---

## 🏷️ Script 4: RAR_PrefixRename-RarReanme(Overwrite).py (Smart Rename)  
### Function  
Analyze RAR internal structure → prepend core content name:  
✅ Skips generic folders (Content, 库文件, data, config)  
✅ Auto-removes existing [prefix] to avoid duplication  
✅ Spaces removed from extracted name (Forest Scene → ForestScene)  
✅ Skips if target filename exists (no overwrite)  
🎯 Use cases: Resource naming standardization, library organization  

### Configuration  
| Setting           | Description                    | Example                       |
| ----------------- | ------------------------------ | ----------------------------- |
| Process directory | Root folder (scans subfolders) | F:\UE Resource Packs          |
| Skip folders      | Dive deeper when found         | Content, 库文件, data, config |

### Steps  
1️⃣ Install dependency: `pip install rarfile` in Command Prompt  
2️⃣ Edit bottom directory path in script  
3️⃣ Double-click → RARs renamed to [ExtractedName]OriginalName.rar  
4️⃣ Check results:  
   - Success: Shows renamed path  
   - Skipped: "Multi-volume"/"Password required"/"No valid name" messages  

⚠️ Notes:  
- **rarfile library required** (install first!)  
- Processes .rar files only (others ignored)  
- Naming logic: Removes existing [prefix] → adds new prefix  

---

## ⚠️ Universal Critical Reminders  
| Issue                             | Solution                                                                                     |
| --------------------------------- | -------------------------------------------------------------------------------------------- |
| "rar.exe not found" in any script | Script uses "Program File" (NO "s") → Modify to match actual install path (usually with "s") |
| Script 4: "ModuleNotFoundError"   | Run: `pip install rarfile`                                                                   |
| Chinese path errors/garbled text  | Set system locale to Chinese (Control Panel → Region → Chinese)                              |
| Process interrupted               | Completed items preserved; Scripts 2/3 show progress for resumption                          |
| First-time use                    | Always test with sample files before batch processing                                        |

---

## 💡 Pro Workflow Combination  
✨ **Full Resource Pack Optimization**:  
1️⃣ Use 【Script 4】to rename all RARs (standardize naming)  
2️⃣ Use 【Script 2】to clean redundant files (purify content)  
3️⃣ Use 【Script 3】to batch extract cover images (generate previews)  
4️⃣ Use 【Script 1】to create hybrid image for core assets (stealth sharing)  

✨ **Safety Protocol**:  
✅ Always backup critical data before processing (10 seconds saves hours!)  
✅ Keep Script 2's CSV report (audit trail / review reference)  
✅ Path reminder: All scripts use "Program File" (NO "s") → Modify configuration to match your actual WinRAR install path!  

---  
📄 Doc Version: v1.0 | 📅 Updated: March 13, 2026  
✨ Precision tools for precise work ✨  
✨ Path note: All scripts use "Program File" (NO "s") → Adjust configuration to match your actual installation ✨