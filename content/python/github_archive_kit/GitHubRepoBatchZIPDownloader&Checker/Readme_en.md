# GitHub Repo Batch ZIP Downloader & Integrity Checker

This repository provides a complete set of Python tools for **batch downloading GitHub repositories as ZIP archives** (auto-detecting latest versions, resuming support, cleaning old versions) and **bidirectional integrity checking** (finding missing repos and extra ZIP files). Ideal for offline backup and batch archiving of GitHub repositories.

## ✨ Features

### 📦 Batch Downloader (`StartDownload.py`)
- ✅ Supports reading GitHub repo URLs from a text file
- ✅ **Auto-detect latest version**: fetches default branch and latest commit SHA via GitHub API
- ✅ **Smart skip**: if the latest version already exists locally, skip download
- ✅ **Auto-clean old versions**: when a repo updates, old ZIPs are moved to `old_versions/`
- ✅ **Manual file recognition**: manually placed ZIPs following naming rules are recognized and skip duplicate downloads
- ✅ **Retry mechanism**: automatically retries on network timeouts, connection errors (up to 3 times)
- ✅ **GitHub Token support**: configure via environment variable or `.github_token` file to increase API rate limit
- ✅ **Progress visualization**: uses `tqdm` if installed
- ✅ **Atomic config saving**: safely updates status file to prevent corruption
- ✅ **Detailed logging**: all operations logged to `zip_download_log.txt`

### 🔍 Integrity Checker (`CheckMissing.py`)
- ✅ **Bidirectional check**:
  - Find which repos from the URL list are missing (not downloaded)
  - Find which ZIP files exist but are not in the URL list (extra)
- ✅ **Case‑insensitive matching**: `Owner/Repo` matches `owner_repo@sha.zip` or `OWNER_REPO.zip`
- ✅ **Supports two ZIP naming formats**:
  - `{owner}_{repo}@{short_sha}.zip` (default downloader format)
  - `{owner}_{repo}.zip` (manual naming compatible)
- ✅ **Automatic deduplication**: duplicate URLs in input file are warned and deduplicated
- ✅ **Clear output reports**: generates separate lists for missing and extra files

## 📁 File Structure
```
├── StartDownload.py # Main downloader (recommended)
├── GitHubZipDownloader.py # Alternative downloader (same functionality)
├── CheckMissing.py # Integrity checker
├── README.md # This file
│
├── (auto‑generated at runtime)
├── old_versions/ # Old version ZIPs auto‑moved here
├── zip_download_status.json # Download status (completed, failed)
├── zip_download_log.txt # Operation log
├── .github_token # (optional) GitHub token file
└── (downloaded ZIP files) # Format: {owner}_{repo}@{short_sha}.zip
```

> **Note**: `GitHubZipDownloader.py` and `StartDownload.py` are functionally identical (only minor comment differences). Use `StartDownload.py` – recommended.

## 🔧 Requirements

- Python 3.6 or higher
- `requests` library (optional `tqdm` for progress bar)

Install dependencies:

    pip install requests tqdm

## 🚀 Quick Start

### 1. Prepare URL list file

Create a text file (e.g., `repos.txt`) with one GitHub repo URL per line. Supported formats:

    https://github.com/owner/repo
    https://github.com/owner/repo.git
    https://github.com/owner/repo/

Empty lines and lines starting with `#` are ignored.

Example `repos.txt`:

    # This is a comment
    https://github.com/facebook/react
    https://github.com/vuejs/vue
    https://github.com/tensorflow/tensorflow

### 2. Run the downloader

Drag and drop the URL list file onto `StartDownload.py`, or run from command line:

    python StartDownload.py /path/to/repos.txt

What it does:
- Parses each URL
- Gets default branch (`main` or `master`) and latest commit SHA
- Generates ZIP filename: `{owner}_{repo}@{short_sha}.zip`
- If the file already exists locally, skips download
- Otherwise downloads and saves
- If an older version (different SHA) of the same repo exists, moves it to `old_versions/`
- Records completed/failed URLs in `zip_download_status.json`

### 3. Run the integrity checker

After downloading (or during regular maintenance), run `CheckMissing.py` to check for missing or extra files.

**First**, edit the configuration section at the top of `CheckMissing.py`:

    INPUT_FILE = r"D:\0lib2\All.txt"      # Your GitHub URL list file
    ZIP_ROOT = r"D:\0libZip"              # Directory where ZIP files are stored
    OUTPUT_MISSING = r"D:\0lib2\miss.txt" # Output file for missing repos
    OUTPUT_EXTRA = r"D:\0lib2\extra.txt"  # Output file for extra ZIPs
    VERBOSE = False                       # Whether to print detailed matching

Then run:

    python CheckMissing.py

What it does:
- Reads URL list, extracts all `owner/repo` prefixes (lowercased)
- Scans ZIP directory, extracts prefixes from ZIP filenames (also lowercased)
- Outputs missing URLs to `miss.txt`
- Outputs extra ZIP filenames to `extra.txt` (plus orphaned ZIPs that cannot be parsed)

## ⚙️ Configuration

### GitHub Token (optional, highly recommended)

Without authentication, GitHub API limits are **60 requests per hour** per IP. With a token, the limit increases to **5000 per hour**.

**Method 1: Environment variable**

    # Windows (CMD)
    set GITHUB_TOKEN=your_token_here

    # Linux / macOS
    export GITHUB_TOKEN=your_token_here

**Method 2: File configuration**
Create a file named `.github_token` in the same directory as the downloader, containing only the token string (no spaces, no newlines).

> How to get a token? GitHub Settings → Developer settings → Personal access tokens → Generate new token (no permissions needed, only for public repo access)

### Adjustable parameters (in `StartDownload.py`)

    self.max_retries = 3        # Maximum retries
    self.retry_delay = 5        # Retry delay (seconds)
    self.download_timeout = 60  # Download timeout (seconds)

## 📄 Output Description

### Downloaded ZIP files
- Naming: `{owner}_{repo}@{short_sha}.zip`  
  Example: `facebook_react@5f6c8e7.zip`
- Location: same directory as `StartDownload.py`

### `old_versions/` directory
When a repository updates, older ZIP files are moved here. If a filename conflict occurs, a timestamp is added, e.g., `facebook_react@3a4b5c6_20250101_120000.zip`.

### `zip_download_status.json`
Records download status for each URL. Example format:

    {
      "completed": {
        "https://github.com/facebook/react": {
          "zip_file": "facebook_react@5f6c8e7.zip",
          "commit_sha": "5f6c8e7a9b...",
          "branch": "main"
        }
      },
      "failed": {
        "https://github.com/owner/bad-repo": {
          "error": "invalid_url",
          "retry_count": 3,
          "final": true
        }
      },
      "last_updated": "2025-01-01T12:00:00"
    }

### `zip_download_log.txt`
Detailed operation log with timestamps, per‑repo processing and errors.

### Checker outputs
- `miss.txt`: Missing repo URLs (can be used as input to run the downloader again)
- `extra.txt`: Extra ZIP filenames (repos not in URL list or leftover files), plus orphaned ZIPs with unparseable names.

## ⚠️ Notes

1. **Case‑insensitive matching**: The checker ignores case, so `Owner/Repo` matches `owner_repo.zip`. However, the downloader preserves original case from the URL path in the generated ZIP filename.
2. **API rate limiting**: Without a token, if you have many repos (>60), the tool automatically waits for rate limit reset. Using a token is strongly recommended.
3. **Network issues**: The tool retries transient errors (timeouts, connection problems). Permanent errors (404, auth) are marked as failed and skipped.
4. **Manual ZIP placement**: If you manually place a ZIP following the naming rules (`{owner}_{repo}@{sha}.zip` or `{owner}_{repo}.zip`), the downloader will recognize it and skip downloading. The checker will still validate against the URL list.
5. **Interrupt recovery**: Press `Ctrl+C` to safely interrupt. Any incomplete ZIP is deleted; the status file retains completed records.
6. **Public repos only**: Designed for public repositories. For private repos, you need a token with appropriate permissions and may need to adjust API headers (token support is already present).

## 📝 FAQ

**Q: Why does the downloaded ZIP filename contain a short hash?**  
A: The hash is the first 7 characters of the latest commit SHA. This version identifier prevents overwriting when a repo updates; old versions are moved to `old_versions`.

**Q: How to re-download failed repositories?**  
A: Simply run the downloader again. It will skip already successful repos and only process failed/unprocessed URLs.

**Q: What does "cannot parse prefix" mean in the checker output?**  
A: It means the ZIP filename does not match the expected pattern `{owner}_{repo}[@{...}].zip`. The checker cannot determine which repo it belongs to; you need to rename or delete it manually.

**Q: Does this support GitHub Enterprise on‑premises?**  
A: Currently only `github.com` is supported. To support Enterprise, you can modify the domain checking logic in the code.

## 📜 License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it.

---

**Enjoy!** For issues, please open an Issue.