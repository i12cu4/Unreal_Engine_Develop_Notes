# 🎬 Video Quick Editing And 🎬 Video Sequential Merger

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)  
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)  
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/)

> Command-line tools designed for efficient video processing | **Stream copy with zero parameter modification** | **Smart filename handling** | **No residual temporary files**

---

## 🎬 Video Quick Editing Description

## ✨ Core Features

| Feature                           | Description                                                                                         |
| --------------------------------- | --------------------------------------------------------------------------------------------------- |
| 🔒 **Zero Parameter Modification** | Full `-c copy` stream copying, 100% preserves original frame rate/resolution/codec/audio parameters |
| ⏱️ **Precise Time Trimming**       | Strictly trims by `start→end` timestamps (e.g., `4:30→4:41` = exactly 11 seconds of content)        |
| 🧠 **Smart Filename Handling**     | Input video names can omit extensions (input `Video` automatically matches `Video.mp4`)             |
| 📁 **Standardized Naming**         | Export files automatically add source filename prefix: `source_filename_identifier.extension`       |
| 🧹 **Residue-Free Cleanup**        | Temporary files/concat files automatically cleaned, directories always stay tidy                    |
| 🔄 **Efficient Looping**           | Automatically enters next round after processing, no repeated confirmations needed                  |
| 🌐 **Chinese Friendly**            | Perfect support for Chinese paths, Chinese filenames, and Chinese prompts                           |
| 🛡️ **Safety Protection**           | Overwrite confirmation, illegal character blocking, automatic exception cleanup                     |

---

## 📋 Environment Requirements

- **Operating System**: Windows 7/10/11
- **Python**: Version 3.6 or higher
- **FFmpeg**:
  - Default path: `C:\Program File\ffmpeg\bin\ffmpeg.exe`
  - [FFmpeg Official Download](https://ffmpeg.org/download.html)

> 💡 **Important Note**: If your FFmpeg is installed in a different location, modify the `FFMPEG_PATH` variable on line 7 of `main.py`

---

## 🎬 Video Sequential Merger Description

## ✨ Core Features

| Feature                      | Description                                                                                                |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 🔢 **Precise Order Control**  | Strictly merges in user's **addition order** (not filename/system sort), drag-and-drop determines sequence |
| 💬 **Interactive Guidance**   | Real-time terminal prompts with clear feedback per step (✅ success/❌ error messages)                       |
| 🔒 **Zero Quality Loss**      | Full `-c copy` stream copying, 100% preserves original encoding parameters                                 |
| 🧹 **Smart Error Prevention** | Automatically skips duplicate files/invalid paths, instant validation before adding                        |
| 📅 **Safe Naming**            | Output filename format = `year-month-day-hour-minute-second.mp4` (absolutely unique)                       |
| 🌐 **Full Chinese Support**   | Perfect handling of Chinese paths/filenames/terminal prompts                                               |
| 🛡️ **Safe Cleanup**           | Temporary list files automatically deleted, no residues                                                    |

---

## 📋 Usage Guide

### ✅ Standard Workflow
1. **Launch Program**  
   - Drag the **first video** onto the program icon → terminal automatically opens
   
2. **Add Subsequent Videos (repeat)**  
   - Drag the **next video** into the terminal window → **press Enter to confirm**  
   - Terminal shows: `✅ Added (2): video2.mp4`  
   - Repeat to add all videos (sequence = drag order)
   
3. **Trigger Merge**  
   - After adding all videos, **press Enter directly (empty input)**  
   - Program automatically validates quantity → starts lossless merge
   
4. **Get Result**  
   - Merged file saved in the **directory of the first video**  
   - Filename example: `2026-03-13-14-30-22.mp4`

### ⚠️ Critical Notes
- **Enter confirmation required**: Must press Enter after each drag (terminal input mechanism limitation)
- **Order is critical**: Merge sequence = **user addition order** (not filename/timestamp sort)
- **Minimum 2 videos**: Shows "at least 2 videos needed" if only one video is added
- **Duplicate file blocking**: Automatically skips and alerts for same-path videos
- **Lossless requirement**: All videos must have consistent encoding parameters (otherwise merge fails)

> 💡 **Tip**: Shares the same FFmpeg path configuration with the trimming tool (modify `FFMPEG_PATH` on line 7 of `merge_tool.py`)

---

## 🌰 Complete Interaction Example
```text
============================================================
🎬 Merge mode started | Starting video: opening.mp4
📍 Output directory: D:\Videos
💡 Drag the【next】video file into this window (or enter path), press Enter to confirm
💡 Press Enter directly (empty input) to start merging all added videos
============================================================

📎 Drag next video (or press Enter to finish adding): [User drags main.mp4 then presses Enter]
✅ Added (2): main.mp4

📎 Drag next video (or press Enter to finish adding): [User drags ending.mp4 then presses Enter]
✅ Added (3): ending.mp4

📎 Drag next video (or press Enter to finish adding): [User presses Enter directly]
============================================================
🔧 Starting merge of 3 videos (lossless mode)...
💾 Output file: 2026-03-13-14-30-22.mp4
============================================================

✅ Merge successful! File saved to:
   D:\Videos\2026-03-13-14-30-22.mp4

📌 Processed 3 videos total | No re-encoding | Zero quality loss
```

---

## ❓ Frequently Asked Questions
**Q: Why must I press Enter after dragging a video?**  
A: Windows terminal input mechanism requires it—dragging only populates the input field, Enter triggers program reading (system-level limitation, not a program flaw)

**Q: How to adjust merge order?**  
A: Strictly follows **addition order**: earlier drags come first, later drags come after. To adjust, rerun the program and add in your target sequence

**Q: What if merge fails?**  
```diff
- Common causes:
- • Inconsistent video encoding parameters (mixed phone+camera footage)
- • Audio/video stream format conflicts
+ Solutions:
+ 1. Use this tool's【Video Quick Editing】feature to standardize parameters
+ 2. Ensure all videos come from the same device/same settings
`