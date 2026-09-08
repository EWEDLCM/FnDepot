import json
import urllib.request
import urllib.error
import os
from datetime import datetime, timezone, timedelta

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("错误：未找到 GITHUB_TOKEN 环境变量！")
    exit(1)

MAX_FILE_SIZE = 2 * 1024 * 1024
DEAD_REPO_MONTHS = 6

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
    "User-Agent": "Fnpack-Source-Validator"
}

def query_github_api(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"  [API 请求失败]: {url} -> {e}")
        return None

def validate_fnpack_content(json_data):
    if not isinstance(json_data, dict): return False
    if "schema_version" in json_data:
        if str(json_data["schema_version"]) != "2": return False
        source_info, apps = json_data.get("source_info"), json_data.get("apps")
        if not isinstance(source_info, dict) or not isinstance(apps, dict): return False
        if not source_info.get("name") or not source_info.get("author"): return False
        if len(apps) == 0 or len(apps) > 5000: return False
        return True
    else:
        if "source_info" in json_data or "apps" in json_data: return False
        if len(json_data) == 0: return False
        return True

def process_repository(full_name):
    print(f"\n正在审查仓库: {full_name}")
    repo_meta = query_github_api(f"https://api.github.com/repos/{full_name}")
    if not repo_meta: return False
        
    default_branch, pushed_at_str = repo_meta.get("default_branch"), repo_meta.get("pushed_at")
    
    if pushed_at_str:
        pushed_at = datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        months_ago = datetime.now(timezone.utc) - timedelta(days=DEAD_REPO_MONTHS * 30)
        if pushed_at < months_ago:
            print(f"  [拦截] 超过 {DEAD_REPO_MONTHS} 个月未更新。")
            return False
            
    if not default_branch: return False

    raw_url = f"https://raw.githubusercontent.com/{full_name}/refs/heads/{default_branch}/fnpack.json"
    req = urllib.request.Request(raw_url, headers={"User-Agent": "Fnpack-Source-Validator"})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.headers.get('Content-Length') and int(resp.headers.get('Content-Length')) > MAX_FILE_SIZE: return False
            raw_data = resp.read(MAX_FILE_SIZE + 1)
            if len(raw_data) > MAX_FILE_SIZE: return False
            try:
                json_data = json.loads(raw_data.decode('utf-8'))
            except json.JSONDecodeError: return False
            return validate_fnpack_content(json_data)
    except: return False

def main():
    print("开始获取候选名单...")
    candidate_repos = []
    
    data1 = query_github_api("https://api.github.com/search/code?q=filename:fnpack.json&per_page=100")
    if data1: candidate_repos.extend([item["repository"]["full_name"] for item in data1.get("items", [])])
    
    data2 = query_github_api("https://api.github.com/search/code?q=filename:fnpack.json+fork:true&per_page=100")
    if data2: candidate_repos.extend([item["repository"]["full_name"] for item in data2.get("items", [])])
    
    candidate_repos = list(set(candidate_repos))
    print(f"共发现 {len(candidate_repos)} 个候选仓库，开始执行质检...")

    valid_sources = []
    for repo in candidate_repos:
        if process_repository(repo):
            print("  [✓] 质检通过！")
            valid_sources.append(f"https://github.com/{repo}")
        else:
            print("  [x] 质检未通过。")

    valid_sources.sort()
    
    # 【改动重点在这里】
    # 获取 GitHub Actions 的工作区根目录，如果在本地测试没这个变量，就默认存在当前路径(".")
    workspace = os.getenv("GITHUB_WORKSPACE", ".")
    output_file = os.path.join(workspace, "valid_sources.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        for source in valid_sources:
            f.write(source + "\n")
            
    print(f"\n处理完成！有效源已写入 {output_file}")

if __name__ == "__main__":
    main()