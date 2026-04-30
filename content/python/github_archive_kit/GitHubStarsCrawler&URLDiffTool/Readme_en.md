# GitHub Stars Crawler & URL Diff Tool

This repository provides two small utilities:
- **GitHub Stars Crawler**: fetch all starred repository URLs of a given GitHub user.
- **URL Diff Tool**: compare two text files containing URLs and find which URLs are present in the first file but not in the second.

Useful for backing up your starred repos, comparing different collections of repositories, etc.

## ✨ Features

### ⭐ GitHub Stars Crawler (`stars_crawler.py`)
- ✅ Fetches all starred repos via GitHub API (100 items per page)
- ✅ Automatically handles API rate limits (403 error) – waits until limit resets
- ✅ Supports configurable max pages, retry counts, and retry delays
- ✅ Deduplicates URLs automatically
- ✅ Generates two output files: full URL list (`.txt`) and a summary (`_summary.txt`)
- ✅ Friendly progress output showing current page, retry status, and estimated wait time

### 🔍 URL Diff Tool (`url_diff.py`)
- ✅ Reads two text files (one URL per line)
- ✅ Computes the set of URLs that are in file A but NOT in file B
- ✅ Automatic deduplication (set-based)
- ✅ Optional output file to save the result
- ✅ Displays statistics: total in A, total in B, number of unique URLs in A

## 📁 File Structure
```
├── stars_crawler.py # Main stars crawler
├── url_diff.py # URL difference tool
├── README.md # This file
│
├── (generated at runtime)
├── github_stars_<username>all_api.txt # Full URL list
├── github_stars<username>_all_api_summary.txt # Summary report
└── (optional diff output file)
```

## 🔧 Requirements

- Python 3.6 or higher
- `requests` library

Install dependencies:

    pip install requests

## 🚀 Quick Start

### 1. Configure and run the Stars Crawler

Edit the configuration section at the top of `stars_crawler.py`:

    USERNAME = "i12cu4"               # Target username
    OUTPUT_FILE = f"github_stars_{USERNAME}_all_api.txt"
    MAX_PAGES = 10                    # Maximum pages to fetch (100 per page)
    MAX_RETRIES = 500                 # Max retries on errors
    RETRY_DELAY = 5                   # Delay between retries (seconds)
    RATE_LIMIT_WAIT = 3600            # Wait time when rate‑limited (seconds)

Then run:

    python stars_crawler.py

What it does:
- Requests each page from the GitHub API sequentially
- On 403 rate limit, waits intelligently using the `X-RateLimit-Reset` header
- Sleeps 0.5 seconds between pages to be gentle
- Saves all starred repo URLs and a summary report

**Strongly recommended: add a GitHub Personal Access Token (PAT)**  
Add `Authorization: token YOUR_TOKEN` to the `headers` dictionary. This raises the API limit from 60 to 5000 requests per hour. See “Configuration” below.

### 2. Use the URL Diff Tool

Edit the example section at the bottom of `url_diff.py`:

    file_a = r"D:\path\to\fileA.txt"   # Path to file A
    file_b = r"D:\path\to\fileB.txt"   # Path to file B
    output_file = "diff_result.txt"    # Output file (set to None to skip saving)

Run:

    python url_diff.py

Output example:

    A文件总共有 xxx 个网址
    B文件总共有 xxx 个网址
    A文件中独有的网址有 xxx 个

    (then lists all unique URLs if any)

## ⚙️ Configuration

### GitHub Personal Access Token (strongly recommended)

Without authentication, GitHub API limits are **60 requests per hour**. Users with many stars (>600) will quickly hit the limit. With a token, the limit is **5000 per hour**.

**How to add the token** in `stars_crawler.py`:

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token ghp_xxxxxxxxxxxxx'   # replace with your actual token
    }

How to get a token:  
GitHub Settings → Developer settings → Personal access tokens → Generate new token (no permissions needed, only for public API access).

### Crawler parameters

- `MAX_PAGES`: If you have fewer than 100 stars, set to 1. The API returns at most 1000 items (10 pages), but the tool won’t exceed `MAX_PAGES`.
- `MAX_RETRIES`: Number of retries for network errors or non‑200/403 status codes. Keep it high (e.g., 500) to avoid interruption from temporary issues.
- `RATE_LIMIT_WAIT`: Default wait time (seconds) when a 403 response does not include a `X-RateLimit-Reset` header. When the header is present, the tool waits precisely until reset.

### Diff tool parameters

- Both input files should be plain text with one URL per line (any URL format is fine, not limited to GitHub).
- `output_file`: If provided, the result is written to that file; if `None` or empty, no file is saved.

## 📄 Output Description

### Stars Crawler outputs

1. **Main file**: `github_stars_<username>_all_api.txt`  
   One URL per line, sorted.  
   Example:

        https://github.com/facebook/react
        https://github.com/vuejs/vue

2. **Summary file**: `github_stars_<username>_all_api_summary.txt`  
   Contains crawl time, total count, first 10 URLs, etc.

### Diff tool output

- If `output_file` is specified, the file contains the unique URLs from A (one per line).
- Regardless of file saving, the console prints statistics and the list (if the unique set is small).

## ⚠️ Notes

1. **API rate limiting**: Without a token, crawling more than 60 stars will almost certainly trigger rate limiting. The tool waits until the limit resets, but that can take up to an hour. **Using a token is strongly recommended**.
2. **Pagination limit**: The GitHub API returns at most 100 items per page and 1000 total (10 pages). If you have more than 1000 starred repos, you will need a different approach (e.g., GraphQL or multiple runs).
3. **Encoding**: Both tools use UTF‑8 encoding for reading and writing. If your files use a different encoding, modify the `encoding` parameter in `open()`.
4. **Network stability**: The crawler retries on network errors, but ensure `MAX_RETRIES` is large enough to survive temporary outages.

## 📝 FAQ

**Q: The crawler stops with “GitHub API rate limit” – what should I do?**  
A: This is normal. The tool waits automatically for the limit to reset (usually one hour). To avoid waiting, add a personal access token as described above.

**Q: Not all my starred repos are saved – why?**  
A: Check `MAX_PAGES`. If you have more than 1000 stars, the API only returns the first 1000 (GitHub restriction). In that rare case, consider using GraphQL or splitting the crawl over time.

**Q: Does the order of files A and B matter in the diff tool?**  
A: Yes. The tool finds URLs that are in A but not in B. To find URLs in B but not in A, simply swap the two arguments.

**Q: Can I use the diff tool for non‑URL text?**  
A: Yes. Any line‑based text works – the tool performs set difference.

## 📜 License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it.

---

**Enjoy!** For issues, please open an Issue.