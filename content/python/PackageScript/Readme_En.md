## Compressed Archive Conversion / CRUD Operations / Encryption & Decryption

### 7Z - Code primarily handling 7Z archive operations
- Encryption
- Anomaly detection
- Decryption
- Convert to RAR format (with progress bar)

### RAR - Code primarily handling RAR archive operations
- Delete specified files and folders (WinRar command mode, Rar command mode, hybrid mode)
- Image-in-image detection
- File existence detection (CSV export supported)
- Extract files from archives (jpg/png examples)
- Archive prefix management
- Export hierarchy structure
- Encryption
- Anomaly detection
- Compression
- Secondary compression detection in archives

### ZIP - Code primarily handling ZIP archive operations
- Encryption
- Decryption
- Convert to RAR format (with progress bar)

### More - Additional Features
- Password protection detection (simultaneous check for zip/rar/7z)

### Further Details...

Note-1: Comprehensive details for all programs are documented in respective folder Readme files. This summary avoids redundancy.

Note 0: Before executing any code, ensure your system has "WinRar", "7-Zip", and "Python3" properly installed and configured.

Note 1: I haven't added WinRar and 7Z to the Path environment variables (Sysdm.cpl). Instead, Python directly calls them using absolute paths.

Note 2: I installed WinRar and 7Z to **C:\Program File**, note it's "File" not the system default **C:\Program Files**.

Note 3: When attempting to read archives with code (except decryption scripts), ensure the archive is NOT password-protected. Otherwise, the process may hang (simply terminating the script won't work—you'll need Task Manager to kill the process, referencing "Associated Handles" in "Resource Monitor").

Note 4: I haven't expanded functionality for 7Z and ZIP formats extensively because RAR offers superior stability, compatibility, and compression/decompression speed compared to ZIP and 7Z. I prefer converting target archives to RAR format before further processing. These scripts meet my current needs. If you require more ZIP/7Z operations, contributions are welcome.

Note 5: Some scripts modify files irreversibly. Always back up or test before execution. I cannot guarantee all scripts will meet user expectations despite extensive testing with numerous samples. Proceed with caution.

Note 6: This library might have delayed updates. For real-time latest content, visit my [main repository](https://github.com/i12cu4/Unreal_Engine_Develop_Notes/tree/main/content/python/PackageScript)

### Even More...

I've developed portable versions of 7Z and WinRAR (converted to binary stored within code) in another repository, see [here](https://github.com/i12cu4/PortableExecutableFile)

Examples:
- [Convert to RAR (Python script)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E7%9B%AE%E6%A0%87%E6%BA%90%E4%BB%A3%E7%A0%81/%E8%BD%ACRAR.py) [Convert to RAR (EXE program)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E6%89%93%E5%8C%85%E7%BB%93%E6%9E%9C/%E8%BD%ACRAR.exe)  
  Drag and drop multiple files/folders onto the py/exe file to automatically convert 7z/zip to rar format (non-7z/zip files skipped). For folders, all subfiles are processed recursively.

- [Archive Extraction (Python script)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E7%9B%AE%E6%A0%87%E6%BA%90%E4%BB%A3%E7%A0%81/%E5%8E%8B%E7%BC%A9%E5%8C%85%E8%A7%A3%E5%8E%8B.py) [Archive Extraction (EXE program)](https://github.com/i12cu4/PortableExecutableFile/blob/main/%E6%89%93%E5%8C%85%E7%BB%93%E6%9E%9C/%E5%8E%8B%E7%BC%A9%E5%8C%85%E8%A7%A3%E5%8E%8B.exe)  
  Drag and drop multiple files/folders onto the py/exe file to automatically extract 7z/zip/rar archives (non-archive files skipped). For folders, all subfiles are processed recursively.

Additional solutions not elaborated here.