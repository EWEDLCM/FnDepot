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
    "BearHero520/FnDepot",
]

# 禁止冒充官方的关键字（不区分大小写与首尾空格）
FORBIDDEN_AUTHORS = {"fndepot"}

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

def is_forbidden_identity(name):
    """检测作者/开发者/发布者是否冒用官方身份"""
    if not name or not isinstance(name, str):
        return False
    norm = name.strip().lower()
    return norm in FORBIDDEN_AUTHORS or norm.replace(" ", "") == "fndepot"

def validate_v1_app(app_key, app_data):
    """验证 V1 单个应用的字段合法性"""
    if not isinstance(app_data, dict):
        return False, "应用数据不是字典"

    # 必填字段
    for f in ["display_name", "desc", "version"]:
        val = app_data.get(f)
        if val is None or str(val).strip() == "":
            return False, f"缺少必填字段 {f}"

    # 冒用官方名称校验
    for f in ["author", "distributor"]:
        if is_forbidden_identity(app_data.get(f)):
            return False, f"存在冒充官方违规命名 ({f}: {app_data.get(f)})"

    # install_type：仅支持空、存储空间(storage)、系统空间(root/system)
    inst = str(app_data.get("install_type") or "").strip().lower()
    if inst not in ["", "存储空间", "storage", "系统空间", "root", "system"]:
        return False, f"install_type 格式不合法: {app_data.get('install_type')}"

    # isdocker / isroot 布尔合法性
    for b_key in ["isdocker", "is_docker", "isroot", "is_root"]:
        if b_key in app_data:
            val = app_data[b_key]
            if not isinstance(val, bool) and str(val).strip().lower() not in ["true", "false", "0", "1"]:
                return False, f"{b_key} 格式不合法: {val}"

    # run_as
    run_as = str(app_data.get("run_as") or "").strip().lower()
    if run_as not in ["", "package", "root"]:
        return False, f"run_as 格式不合法: {app_data.get('run_as')}"

    return True, "ok"

def validate_v2_app(app_key, app_data):
    """验证 V2 单个应用的字段合法性"""
    if not isinstance(app_data, dict):
        return False, "应用数据不是字典"

    # 必填字段
    for f in ["display_name", "desc"]:
        val = app_data.get(f)
        if val is None or str(val).strip() == "":
            return False, f"缺少必填字段 {f}"

    # 冒用官方名称校验
    for f in ["maintainer", "distributor"]:
        if is_forbidden_identity(app_data.get(f)):
            return False, f"存在冒充官方违规命名 ({f}: {app_data.get(f)})"

    # install_type：仅允许空字符串或 root
    inst = str(app_data.get("install_type") or "").strip().lower()
    if inst not in ["", "root"]:
        return False, f"install_type 格式不合法: {app_data.get('install_type')}"

    # run_as：仅允许 package 或 root
    run_as = str(app_data.get("run_as") or "").strip().lower()
    if run_as not in ["package", "root"]:
        return False, f"run_as 格式不合法: {app_data.get('run_as')}"

    # is_docker：必须是布尔值
    if "is_docker" not in app_data or not isinstance(app_data["is_docker"], bool):
        return False, f"is_docker 必须为布尔值"

    return True, "ok"

def parse_and_fingerprint(json_data):
    """提取指纹：返回 (是否合格, name集合, signature集合, source_version)"""
    if not isinstance(json_data, dict): return False, set(), set(), None
    
    apps_dict = {}
    source_ver = None
    if "schema_version" in json_data:
        if str(json_data["schema_version"]) != "2": return False, set(), set(), None
        source_info, apps = json_data.get("source_info"), json_data.get("apps")
        if not isinstance(source_info, dict) or not isinstance(apps, dict): return False, set(), set(), None
        if not source_info.get("name") or not source_info.get("author"): return False, set(), set(), None
        
        # 规则2：禁止源作者命名为 fndepot
        if is_forbidden_identity(source_info.get("author")):
            print(f"  [x] 拦截冒名违规源：源作者命名为 {source_info.get('author')}")
            return False, set(), set(), None
            
        if len(apps) == 0 or len(apps) > 5000: return False, set(), set(), None
        apps_dict = apps
        source_ver = "v2"
    else:
        if "source_info" in json_data or "apps" in json_data: return False, set(), set(), None
        if len(json_data) == 0: return False, set(), set(), None
        apps_dict = json_data
        source_ver = "v1"

    app_names = set()
    app_sigs = set()
    valid_apps_count = 0

    for k, v in apps_dict.items():
        # 规则1：应用字段格式与合法性校验
        if source_ver == "v1":
            ok, reason = validate_v1_app(k, v)
        else:
            ok, reason = validate_v2_app(k, v)

        if not ok:
            # 单个应用校验失败，跳过该应用
            continue

        valid_apps_count += 1
        n_name = normalize_name(k)
        app_names.add(n_name)
        
        # 提取版本签名
        version = ""
        if isinstance(v, dict):
            if source_ver == "v1":
                version = v.get("version", "")
            else:
                releases = v.get("releases", {})
                if isinstance(releases, dict) and releases:
                    # 取最新或任意版本
                    version = sorted(releases.keys())[-1]
                else:
                    version = v.get("version", "")
                    
        n_ver = normalize_version(version)
        app_sigs.add(f"{n_name}|{n_ver}")
        
    # 规则1（重要）：如果整个源里没有一个合规应用（全部失败），则该源直接排除
    if valid_apps_count == 0:
        print("  [x] 拦截源：源内没有任何符合规范的有效应用（全部失败）。")
        return False, set(), set(), None

    return True, app_names, app_sigs, source_ver

def fetch_repo_data(full_name):
    """获取仓库元数据、文件并提取指纹，返回字典。如果不合格返回 None"""
    print(f"\n[第1阶段: 质检] 正在审查仓库: {full_name}")
    repo_meta = query_github_api(f"https://api.github.com/repos/{full_name}")
    if not repo_meta: return None
        
    default_branch, pushed_at_str = repo_meta.get("default_branch"), repo_meta.get("pushed_at")
    
    # 死亡判定
    if pushed_at_str:
        pushed_at = datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        months_ago = datetime.now(timezone.utc) - timedelta(days=DEAD_REPO_MONTHS * 30)
        if pushed_at < months_ago:
            print(f"  [拦截] 死仓库 (超过 {DEAD_REPO_MONTHS} 个月未更新)。")
            return None
            
    if not default_branch: return None

    # 文件拉取与校验
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
                print("  [x] 内容/格式未通过质检校验。")
                return None

            # 对 v1 源进行目录结构合规校验：根目录下必须有以其 app_id 命名的子目录
            if source_ver == "v1":
                tree_meta = query_github_api(f"https://api.github.com/repos/{full_name}/git/trees/{default_branch}")
                if not tree_meta or "tree" not in tree_meta:
                    print("  [x] 无法获取仓库文件树，v1 目录校验失败。")
                    return None
                repo_dirs_lower = {it["path"].lower() for it in tree_meta.get("tree", []) if it.get("type") == "tree"}
                missing_dirs = [k for k in json_data.keys() if isinstance(json_data[k], dict) and k.lower() not in repo_dirs_lower]
                matched_count = len(names) - len(missing_dirs)
                if matched_count == 0:
                    print(f"  [x] 目录结构不合规 (v1 源缺少应用子目录，缺失: {missing_dirs})。")
                    return None
                
            print(f"  [✓] 质检通过 ({source_ver})！提取到 {len(names)} 个有效应用指纹。")
            
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
    """计算两集合的重叠率 (分母为较小集合长度)"""
    if not set1 or not set2: return 0.0
    intersection = len(set1.intersection(set2))
    smaller_len = min(len(set1), len(set2))
    return intersection / smaller_len if smaller_len > 0 else 0.0

def process_overlap(repos):
    """第2阶段：血缘与重复剔除逻辑 (O(N^2) 对撞)"""
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
            
            # 血缘判定：是否属于同一家族 (A是B的fork，或B是A的fork，或同宗)
            is_related = False
            if repoA["parent"] == repoB["full_name"] or repoB["parent"] == repoA["full_name"]:
                is_related = True
            elif repoA["parent"] and repoB["parent"] and repoA["parent"] == repoB["parent"]:
                is_related = True
                
            is_high_risk = False
            
            # 判定门槛
            if is_related:
                # 规则3：Fork 血缘重复率收紧至 ≥50% (名称) 或 ≥30% (精确)
                if name_rate >= 0.50 or sig_rate >= 0.30:
                    is_high_risk = True
            else:
                # 无 Fork 身份（普通重复）：≥85% (名称) 且 ≥70% (精确)
                if name_rate >= 0.85 and sig_rate >= 0.70:
                    is_high_risk = True
                    
            if is_high_risk:
                loser = None
                
                # 规则1: Fork 特权覆盖默认 (Fork 永远输给上游原创)
                if is_related and repoA["is_fork"] != repoB["is_fork"]:
                    loser = repoA if repoA["is_fork"] else repoB
                else:
                    # 规则2: 默认后来者输 (比较 created_at)
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
    
    # 1. 仓库搜索（全量召回带 fndepot 的源，包含驼峰与连字）
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

    # 2. 保留代码搜索作为补充
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

