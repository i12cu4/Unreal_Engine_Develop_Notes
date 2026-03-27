# Compressed Archive Password Detector (7-Zip)

## Core Features
- Silent directory scan for password-protected `.rar`, `.zip`, `.7z` files
- Smart filtering: distinguishes real encryption from errors (corruption/path issues)
- Outputs ONLY encrypted file paths (one per line, pipe-friendly)
- 30-second timeout per file (prevents hangs)

## Configuration
Edit script's first line:  
`SEVEN_ZIP_PATH = r"C:\Program Files\7-Zip\7z.exe"`  
⚠️ Default uses `Program File` (no "s") — adjust to match your installation path

## Usage
Command line only:  
`python ArchivePasswordDetector.py "E:\TargetDirectory"`  
- ✅ Must run via command line (double-click shows no output — console hidden)  
- ✅ Zero output if no encrypted files found  
- ✅ Windows only; requires 7-Zip installed  

## Troubleshooting
| Issue           | Solution                                                                                                                                |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| No output       | 1. Confirm archives exist in directory<br>2. Verify 7-Zip path (`Program Files` vs `Program File`)<br>3. Test with known encrypted file |
| False positives | Script auto-filters "file not found", "not archive" errors                                                                              |
| Runtime errors  | Temporarily comment `hide_console_window()` to view errors                                                                              |

## Workflow Integration
Pre-check in RAR Toolkit pipeline:  
1. Detect encrypted files → manual review or decrypt via `RAR-Decryption.py`  
2. If clean → proceed: `RAR-IntegrityCheck` → `RAR-NestedArchiveCheck` → `ExportHierarchy