import json
import urllib.request
import urllib.error
import urllib.parse
import time
import os
from datetime import datetime, timezone, timedelta

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("错误：未找到 GITHUB_TOKEN 环境变量！")
    exit(1)

MAX_FILE_SIZE = 2 * 1024 * 1024
DEAD_REPO_MONTHS = 6

BLACKLIST = [
    "Brian099/fn_fpk_packages",
]

WHITELIST = [
]

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
    except urllib.error.HTTPError as e:
        print(f"  [API 请求失败]: {url} -> HTTP Error {e.code}")
        return None
    except Exception as e:
        print(f"  [API 请求失败]: {url} -> {e}")
        return None

def normalize_name(name):
    return name.lower().replace(" ", "") if name else ""

def normalize_version(ver):
    ver = str(ver).strip()
    if ver.lower().startswith('v'):
        ver = ver[1:]
    return ver

def parse_and_fingerprint(json_data):
    if not isinstance(json_data, dict): return False, set(), set(), None
    
    apps_dict = {}
    source_version = None
    if "schema_version" in json_data:
        if str(json_data["schema_version"]) != "2": return False, set(), set(), None
        source_info, apps = json_data.get("source_info"), json_data.get("apps")
        if not isinstance(source_info, dict) or not isinstance(apps, dict): return False, set(), set(), None
        if not source_info.get("name") or not source_info.get("author"): return False, set(), set(), None
        if len(apps) == 0 or len(apps) > 5000: return False, set(), set(), None
        apps_dict = apps
        source_version = "v2"
    else:
        if "source_info" in json_data or "apps" in json_data: return False, set(), set(), None
        if len(json_data) == 0: return False, set(), set(), None
        apps_dict = json_data
        source_version = "v1"

    app_names = set()
    app_sigs = set()
    for k, v in apps_dict.items():
        n_name = normalize_name(k)
        app_names.add(n_name)
        
        version = v.get("version", "") if isinstance(v, dict) else ""
        n_ver = normalize_version(version)
        app_sigs.add(f"{n_name}|{n_ver}")
        
    return True, app_names, app_sigs, source_version

def fetch_repo_data(full_name):
    print(f"\n[第1阶段: 质检] 正在审查仓库: {full_name}")
    repo_meta = query_github_api(f"https://api.github.com/repos/{full_name}")
    if not repo_meta: return None
        
    default_branch = repo_meta.get("default_branch")
    pushed_at_str = repo_meta.get("pushed_at")
    
    if pushed_at_str:
        pushed_at = datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        months_ago = datetime.now(timezone.utc) - timedelta(days=DEAD_REPO_MONTHS * 30)
        if pushed_at < months_ago:
            print(f"  [拦截] 死仓库 (超过 {DEAD_REPO_MONTHS} 个月未更新)。")
            return None
            
    if not default_branch: return None

    raw_url = f"https://raw.githubusercontent.com/{full_name}/refs/heads/{default_branch}/fnpack.json"
    req = urllib.request.Request(raw_url, headers={"User-Agent": "Fnpack-Source-Validator"})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.headers.get('Content-Length') and int(resp.headers.get('Content-Length')) > MAX_FILE_SIZE: return None
            raw_data = resp.read(MAX_FILE_SIZE + 1)
            if len(raw_data) > MAX_FILE_SIZE: return None
            try:
                json_data = json.loads(raw_data.decode('utf-8'))
            except json.JSONDecodeError: return None
            
            is_valid, names, sigs, source_ver = parse_and_fingerprint(json_data)
            if not is_valid:
                print("  [x] JSON 内容/格式未通过校验。")
                return None

            # 对 v1 源进行目录结构合规校验：
            # 根目录下每一个应用（或主要应用）必须有以其 app_id（键名）命名的子目录
            if source_ver == "v1":
                tree_meta = query_github_api(f"https://api.github.com/repos/{full_name}/git/trees/{default_branch}")
                if not tree_meta or "tree" not in tree_meta:
                    print("  [x] 无法获取仓库文件树，v1 目录校验失败。")
                    return None
                repo_dirs_lower = {it["path"].lower() for it in tree_meta.get("tree", []) if it.get("type") == "tree"}
                
                # 检查 fnpack.json 中声明的 app 是否有对应子目录（不区分大小写匹配）
                missing_dirs = [k for k in json_data.keys() if isinstance(json_data[k], dict) and k.lower() not in repo_dirs_lower]
                if missing_dirs:
                    # 如果匹配到的应用目录数为 0，或者缺失比例过高，判定为非合规 v1 源
                    matched_count = len(names) - len(missing_dirs)
                    if matched_count == 0:
                        print(f"  [x] 目录结构不合规 (v1 源缺少应用子目录，缺失: {missing_dirs})。")
                        return None
                    else:
                        print(f"  [!] v1 源部分应用缺少子目录 (已匹配 {matched_count}/{len(names)}，缺失: {missing_dirs})。")
                
            print(f"  [✓] 质检通过 ({source_ver})！提取到 {len(names)} 个应用指纹。")
            
            return {
                "full_name": full_name,
                "is_fork": repo_meta.get("fork", False),
                "parent": repo_meta.get("parent", {}).get("full_name") if repo_meta.get("fork", False) else None,
                "created_at": repo_meta.get("created_at"),
                "names": names,
                "sigs": sigs
            }
    except: 
        print("  [x] 无法读取文件或网络错误。")
        return None

def calc_overlap(set1, set2):
    if not set1 or not set2: return 0.0
    intersection = len(set1.intersection(set2))
    smaller_len = min(len(set1), len(set2))
    return intersection / smaller_len if smaller_len > 0 else 0.0

def process_overlap(repos):
    print("\n[第2阶段: 查重] 开始执行血缘判定与重复源剔除...")
    eliminated = set() 
    
    for i in range(len(repos)):
        repoA = repos[i]
        if repoA["full_name"] in eliminated: continue
            
        for j in range(i + 1, len(repos)):
            repoB = repos[j]
            if repoB["full_name"] in eliminated: continue
                
            name_rate = calc_overlap(repoA["names"], repoB["names"])
            sig_rate = calc_overlap(repoA["sigs"], repoB["sigs"])
            
            is_related = False
            if repoA["parent"] == repoB["full_name"] or repoB["parent"] == repoA["full_name"]:
                is_related = True
            elif repoA["parent"] and repoB["parent"] and repoA["parent"] == repoB["parent"]:
                is_related = True
                
            is_high_risk = False
            
            if is_related:
                if name_rate >= 0.80 or sig_rate >= 0.40:
                    is_high_risk = True
            else:
                if name_rate >= 0.85 and sig_rate >= 0.70:
                    is_high_risk = True
                    
            if is_high_risk:
                loser = None
                if is_related and repoA["is_fork"] != repoB["is_fork"]:
                    loser = repoA if repoA["is_fork"] else repoB
                else:
                    loser = repoA if repoA["created_at"] > repoB["created_at"] else repoB
                
                eliminated.add(loser["full_name"])
                winner_name = repoB["full_name"] if loser == repoA else repoA["full_name"]
                relation_str = "血缘Fork" if is_related else "非血缘抄袭"
                print(f"  [拦截] 发现高度重复 ({relation_str})!")
                print(f"         名称重叠:{name_rate:.1%} 精确重叠:{sig_rate:.1%}")
                print(f"         胜出者 (保留): {winner_name}")
                print(f"         战败者 (剔除): {loser['full_name']}")
                
                if loser == repoA:
                    break 

    return [r["full_name"] for r in repos if r["full_name"] not in eliminated]

def main():
    print("开始获取候选名单...")
    candidate_repos = []
    
    # 1. 仓库搜索（精准召回所有名称包含 fndepot 的源，解决新仓库/0 Star 仓库无代码索引的问题）
    repo_queries = [
        "fndepot",
        "fn depot",
        "fndepot fork:true",
        "fn depot fork:true"
    ]
    for q in repo_queries:
        for page in range(1, 4):
            url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&per_page=100&page={page}"
            data = query_github_api(url)
            if data and "items" in data:
                items = data["items"]
                for item in items:
                    full_name = item.get("full_name", "")
                    if "fndepot" in full_name.lower():
                        candidate_repos.append(full_name)
                if len(items) < 100:
                    break
            else:
                break
            time.sleep(0.5)

    # 2. 保留原有的代码搜索作为补充（召回不以 FnDepot 命名但含有 fnpack.json 的仓库）
    data1 = query_github_api("https://api.github.com/search/code?q=filename:fnpack.json&per_page=100")
    if data1: candidate_repos.extend([item["repository"]["full_name"] for item in data1.get("items", [])])
    
    data2 = query_github_api("https://api.github.com/search/code?q=filename:fnpack.json+fork:true&per_page=100")
    if data2: candidate_repos.extend([item["repository"]["full_name"] for item in data2.get("items", [])])
    
    candidate_repos.extend(WHITELIST)
    candidate_repos = list(set(candidate_repos))
    
    blacklist_lower = [r.lower() for r in BLACKLIST]
    filtered_repos = []
    blocked_count = 0
    for repo in candidate_repos:
        if repo.lower() in blacklist_lower:
            blocked_count += 1
            print(f"  [黑名单] 已剔除违规/受限仓库: {repo}")
        else:
            filtered_repos.append(repo)
            
    candidate_repos = filtered_repos

    print(f"共发现 {len(candidate_repos)} 个候选仓库 (已过滤 {blocked_count} 个黑名单源)。")

    valid_repo_objs = []
    for repo_name in candidate_repos:
        repo_data = fetch_repo_data(repo_name)
        if repo_data:
            valid_repo_objs.append(repo_data)

    final_valid_names = process_overlap(valid_repo_objs)

    final_valid_names.sort()
    valid_sources = [f"https://github.com/{name}" for name in final_valid_names]
    
    workspace = os.getenv("GITHUB_WORKSPACE", ".")
    output_file = os.path.join(workspace, "valid_sources.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        for source in valid_sources:
            f.write(source + "\n")
            
    print(f"\n处理完成！最终输出 {len(valid_sources)} 个纯净源，已写入 {output_file}")

if __name__ == "__main__":
    main()
