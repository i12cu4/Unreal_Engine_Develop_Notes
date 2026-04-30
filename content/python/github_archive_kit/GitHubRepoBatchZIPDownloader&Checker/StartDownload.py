"""
GitHub 仓库批量 ZIP 下载工具（增强版：版本检测、自动更新、手动文件识别、旧版本清理）
使用方法：将包含 GitHub 链接的文本文件拖拽到本程序上执行
"""

import sys
import os
import json
import time
import shutil
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("❌ 缺少 requests 库，请执行：pip install requests")
    input("\n按回车键退出...")
    sys.exit(1)

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class GitHubZipDownloader:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(sys.argv[0] if sys.argv[0] else __file__))
        self.config_file = os.path.join(self.script_dir, 'zip_download_status.json')
        self.temp_config_file = os.path.join(self.script_dir, 'zip_download_status.temp.json')
        self.log_file = os.path.join(self.script_dir, 'zip_download_log.txt')
        self.old_versions_dir = os.path.join(self.script_dir, 'old_versions')

        self.max_retries = 3
        self.retry_delay = 5
        self.download_timeout = 60

        self.status = {
            'completed': {},
            'failed': {},
            'last_updated': ''
        }

        self.current_zip_path = None
        self.branch_cache = {}
        self.github_token = self._get_github_token()

        os.makedirs(self.old_versions_dir, exist_ok=True)
        self.load_config()

    def _get_github_token(self):
        token = os.environ.get('GITHUB_TOKEN', '')
        if token:
            return token
        token_file = os.path.join(self.script_dir, '.github_token')
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
                return token
            except:
                pass
        return None

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    completed_old = loaded.get('completed', {})
                    new_completed = {}
                    for url, value in completed_old.items():
                        if isinstance(value, str):
                            new_completed[url] = {
                                "zip_file": value,
                                "commit_sha": None,
                                "branch": None
                            }
                        else:
                            new_completed[url] = value
                    self.status['completed'] = new_completed
                    self.status['failed'] = loaded.get('failed', {})
                    self.status['last_updated'] = loaded.get('last_updated', '')
                print(f"✅ 已加载配置文件，已完成 {len(self.status['completed'])} 个仓库")
        except Exception as e:
            print(f"⚠️ 加载配置文件失败: {e}")
            self.status = {'completed': {}, 'failed': {}, 'last_updated': ''}

    def save_config_atomic(self):
        try:
            self.status['last_updated'] = datetime.now().isoformat()
            with open(self.temp_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.status, f, indent=2, ensure_ascii=False)
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            os.rename(self.temp_config_file, self.config_file)
            print(f"💾 配置文件已更新 (时间: {self.status['last_updated']})")
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            try:
                if os.path.exists(self.temp_config_file):
                    os.remove(self.temp_config_file)
            except:
                pass

    def log_message(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except:
            pass

    def extract_repo_info(self, url):
        try:
            url = url.strip().rstrip('/')
            if url.endswith('.git'):
                url = url[:-4]
            parsed = urlparse(url)
            if 'github.com' not in parsed.netloc:
                return None, None
            path = parsed.path.strip('/')
            parts = path.split('/')
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1].replace('.git', '')
                return owner, repo
            return None, None
        except Exception as e:
            self.log_message(f"❌ 解析URL失败 {url}: {e}")
            return None, None

    def get_default_branch(self, owner, repo):
        cache_key = f"{owner}/{repo}"
        if cache_key in self.branch_cache:
            return self.branch_cache[cache_key]

        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = self._get_api_headers()
        try:
            resp = requests.get(api_url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                branch = data.get('default_branch')
                if branch:
                    self.branch_cache[cache_key] = branch
                    return branch
            elif resp.status_code == 403 and 'X-RateLimit-Remaining' in resp.headers:
                reset_time = int(resp.headers.get('X-RateLimit-Reset', 0))
                wait = max(reset_time - int(time.time()), 0) + 5
                self.log_message(f"⚠️ GitHub API 速率限制，需等待 {wait} 秒")
                time.sleep(wait)
                return self.get_default_branch(owner, repo)
        except Exception as e:
            self.log_message(f"⚠️ API 获取分支失败: {e}")

        for candidate in ['main', 'master']:
            test_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{candidate}.zip"
            try:
                resp = requests.head(test_url, allow_redirects=True, timeout=10)
                if resp.status_code == 200:
                    self.branch_cache[cache_key] = candidate
                    return candidate
            except:
                continue

        self.branch_cache[cache_key] = None
        return None

    def get_latest_commit_sha(self, owner, repo, branch):
        api_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
        headers = self._get_api_headers()
        try:
            resp = requests.get(api_url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                sha = data.get('commit', {}).get('sha')
                if sha:
                    return sha
            elif resp.status_code == 404:
                self.log_message(f"⚠️ 分支 '{branch}' 不存在于 {owner}/{repo}")
            elif resp.status_code == 403:
                reset_time = int(resp.headers.get('X-RateLimit-Reset', 0))
                wait = max(reset_time - int(time.time()), 0) + 5
                self.log_message(f"⚠️ API 速率限制，需等待 {wait} 秒")
                time.sleep(wait)
                return self.get_latest_commit_sha(owner, repo, branch)
            else:
                self.log_message(f"⚠️ 获取 commit SHA 失败 {api_url}: HTTP {resp.status_code}")
        except Exception as e:
            self.log_message(f"⚠️ 获取 commit SHA 异常: {e}")
        return None

    def _get_api_headers(self):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        return headers

    def get_zip_url(self, owner, repo, branch):
        return f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

    def download_zip(self, url, dest_path):
        try:
            if os.path.exists(dest_path):
                os.remove(dest_path)

            response = requests.get(url, stream=True, timeout=(10, self.download_timeout))
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(dest_path, 'wb') as f:
                if HAS_TQDM and total_size > 0:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(dest_path)) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\r下载进度: {percent:.1f}%", end='', flush=True)
                    if total_size > 0:
                        print()

            if total_size > 0 and os.path.getsize(dest_path) != total_size:
                raise Exception("下载的文件大小与 Content-Length 不匹配")
            return True, None
        except Exception as e:
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except:
                    pass
            return False, str(e)

    def should_retry_error(self, error_msg):
        if not error_msg:
            return False
        error_lower = error_msg.lower()
        retry_keywords = [
            'timeout', 'timed out', 'connection', 'network', 'unreachable',
            'refused', 'reset', 'broken pipe', 'eof', 'rate limit', 'ssl'
        ]
        return any(kw in error_lower for kw in retry_keywords)

    def move_to_old_versions(self, file_path):
        if not os.path.exists(file_path):
            return
        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.old_versions_dir, filename)
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = os.path.join(self.old_versions_dir, f"{base}_{timestamp}{ext}")
        shutil.move(file_path, dest_path)
        self.log_message(f"📦 旧版本已移动到: {dest_path}")

    def clean_old_versions_for_repo(self, owner, repo, current_short_sha):
        """移动同仓库中短 SHA 不等于当前最新版本的所有带版本号文件"""
        pattern = f"{owner}_{repo}@*.zip"
        zip_root = Path(self.script_dir)
        for zip_file in zip_root.glob(pattern):
            name = zip_file.name
            try:
                sha_part = name.split('@')[1].split('.zip')[0]
                if sha_part != current_short_sha:
                    self.move_to_old_versions(str(zip_file))
            except IndexError:
                # 格式不正确，忽略
                pass

    def process_url(self, url, index, total):
        url = url.strip()
        if not url or url.startswith('#') or url.startswith('//'):
            return False

        owner, repo = self.extract_repo_info(url)
        if not owner or not repo:
            self.log_message(f"❌ 无效URL: {url}")
            self.status['failed'][url] = {'error': 'invalid_url', 'retry_count': 0}
            self.save_config_atomic()
            return False

        overall_retry = 0
        last_error = None

        while overall_retry <= self.max_retries:
            if overall_retry > 0:
                self.log_message(f"🔄 整体重试 #{overall_retry}/{self.max_retries} for {url}")
                time.sleep(self.retry_delay)

            branch = self.get_default_branch(owner, repo)
            if not branch:
                error_msg = "无法获取默认分支"
                self.log_message(f"⚠️ {error_msg}: {url}")
                last_error = error_msg
                if not self.should_retry_error(error_msg):
                    break
                overall_retry += 1
                continue

            latest_sha = self.get_latest_commit_sha(owner, repo, branch)
            if not latest_sha:
                error_msg = "无法获取最新 commit SHA"
                self.log_message(f"⚠️ {error_msg}: {url}")
                last_error = error_msg
                if not self.should_retry_error(error_msg):
                    break
                overall_retry += 1
                continue

            short_sha = latest_sha[:7]
            expected_zip_name = f"{owner}_{repo}@{short_sha}.zip"
            expected_zip_path = os.path.join(self.script_dir, expected_zip_name)

            # 检查本地是否已存在最新版本文件（无论是程序下载还是手动放置）
            if os.path.exists(expected_zip_path):
                self.log_message(f"✅ 本地已存在最新版本文件，跳过下载: {expected_zip_name}")
                self.status['completed'][url] = {
                    "zip_file": expected_zip_name,
                    "commit_sha": latest_sha,
                    "branch": branch
                }
                if url in self.status['failed']:
                    del self.status['failed'][url]
                self.save_config_atomic()
                # 清理同仓库的其他旧版本（不同 SHA 的 @*.zip）
                self.clean_old_versions_for_repo(owner, repo, short_sha)
                return True

            # 检查状态记录中的旧版本
            record = self.status['completed'].get(url)
            if record:
                old_zip_name = record.get('zip_file')
                old_sha = record.get('commit_sha')
                old_zip_path = os.path.join(self.script_dir, old_zip_name) if old_zip_name else None

                if old_sha == latest_sha and old_zip_path and os.path.exists(old_zip_path):
                    self.log_message(f"⏭️ 已是最新版本，跳过: {url} -> {old_zip_name} (SHA: {short_sha})")
                    # 虽然跳过，但也清理可能残留的其他旧版本（比如手动遗留的）
                    self.clean_old_versions_for_repo(owner, repo, short_sha)
                    return True
                else:
                    if old_sha != latest_sha:
                        self.log_message(f"🔄 检测到新版本: {url} (旧SHA: {old_sha[:7] if old_sha else '无'} -> 新SHA: {short_sha})")
                        if old_zip_path and os.path.exists(old_zip_path):
                            self.move_to_old_versions(old_zip_path)
                    else:
                        self.log_message(f"⚠️ 文件丢失，重新下载: {url}")
            else:
                self.log_message(f"📦 首次下载: {url} -> {expected_zip_name} (分支: {branch}, SHA: {short_sha})")

            # 下载 ZIP
            zip_url = self.get_zip_url(owner, repo, branch)
            download_success = False
            download_error = None

            for dl_attempt in range(self.max_retries + 1):
                if dl_attempt > 0:
                    self.log_message(f"🔄 下载重试 #{dl_attempt}/{self.max_retries} for {url}")
                    time.sleep(self.retry_delay)

                self.current_zip_path = expected_zip_path
                success, err = self.download_zip(zip_url, expected_zip_path)
                self.current_zip_path = None

                if success:
                    download_success = True
                    break
                else:
                    download_error = err
                    if not self.should_retry_error(err):
                        self.log_message(f"❌ 下载不可重试错误: {err}")
                        break

            if download_success:
                self.log_message(f"✅ 下载成功: {expected_zip_name}")
                self.status['completed'][url] = {
                    "zip_file": expected_zip_name,
                    "commit_sha": latest_sha,
                    "branch": branch
                }
                if url in self.status['failed']:
                    del self.status['failed'][url]
                self.save_config_atomic()
                # 清理同仓库的其他旧版本
                self.clean_old_versions_for_repo(owner, repo, short_sha)
                return True
            else:
                error_msg = f"下载失败: {download_error}"
                self.log_message(f"⚠️ {error_msg}")
                last_error = error_msg
                if not self.should_retry_error(download_error):
                    break
                overall_retry += 1
                continue

        self.log_message(f"❌ 达到最大重试次数 ({self.max_retries})，放弃: {url}")
        self.status['failed'][url] = {
            'error': last_error,
            'retry_count': self.max_retries,
            'final': True
        }
        self.save_config_atomic()
        return False

    def run(self, input_file):
        self.log_message("=" * 60)
        self.log_message("🚀 GitHub ZIP 批量下载工具（增强版：版本检测、自动更新、手动文件识别、旧版本清理）")
        self.log_message(f"📁 脚本目录: {self.script_dir}")
        self.log_message(f"📋 输入文件: {input_file}")

        if not os.path.exists(input_file):
            self.log_message(f"❌ 输入文件不存在: {input_file}")
            return

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

            total = len(urls)
            self.log_message(f"📖 读取到 {total} 个仓库URL")
            if total == 0:
                self.log_message("⚠️ 没有找到有效的URL，程序退出")
                return

            success_count = 0
            fail_count = 0

            for i, url in enumerate(urls, 1):
                self.log_message(f"\n{'-' * 40}")
                self.log_message(f"📦 处理第 {i}/{total} 个: {url}")

                try:
                    if self.process_url(url, i, total):
                        success_count += 1
                    else:
                        fail_count += 1
                except KeyboardInterrupt:
                    self.log_message("\n🛑 用户中断程序")
                    if self.current_zip_path and os.path.exists(self.current_zip_path):
                        self.log_message(f"🧹 清理未完成的 ZIP: {self.current_zip_path}")
                        try:
                            os.remove(self.current_zip_path)
                        except:
                            pass
                    self.save_config_atomic()
                    sys.exit(1)
                except Exception as e:
                    self.log_message(f"💥 处理URL时发生意外错误: {url} - {str(e)}")
                    fail_count += 1

            self.log_message("\n" + "=" * 60)
            self.log_message(f"📊 下载完成总结:")
            self.log_message(f"✅ 成功: {success_count} 个")
            self.log_message(f"❌ 失败: {fail_count} 个")
            self.log_message("🏁 程序执行完毕")

        except Exception as e:
            self.log_message(f"❌ 读取输入文件时发生错误: {e}")
        finally:
            self.save_config_atomic()


def main():
    if len(sys.argv) < 2:
        print("❌ 错误：请将包含GitHub链接的文本文件拖拽到本程序上执行")
        print("📋 用法示例：将 'repos.txt' 文件拖到本程序图标上")
        input("\n按回车键退出...")
        sys.exit(1)

    input_file = sys.argv[1]
    print(f"📥 接收到的文件: {input_file}")

    try:
        downloader = GitHubZipDownloader()
        downloader.run(input_file)
    except KeyboardInterrupt:
        print("\n🛑 程序被用户中断")
    except Exception as e:
        print(f"💥 程序发生严重错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n按回车键退出...")


if __name__ == "__main__":
    main()