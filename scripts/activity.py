"""采集指定公开项目，每个北京时间日期保存一次真实观测。"""

from datetime import datetime
import json
import os
from pathlib import Path
import random
from statistics import NormalDist
import subprocess
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

PROJECTS = (
    "LittleSixNine/FrameMatter",
    "LittleSixNine/PhotoTrail",
    "LittleSixNine/FilmLog",
    "LittleSixNine/Pawzz-video-downloader",
    "LittleSixNine/photocut",
)
ZONE = ZoneInfo("Asia/Shanghai")


def daily_commit_count():
    normal = NormalDist(mu=3, sigma=1)
    counts = range(1, 6)
    # 截断到 0.5～5.5 后按整数区间取概率，避免越界值堆积在两端。
    weights = [normal.cdf(count + 0.5) - normal.cdf(count - 0.5) for count in counts]
    return random.choices(counts, weights=weights, k=1)[0]


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "project-observatory"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request("https://api.github.com" + path, headers=headers), timeout=20) as response:
        return json.load(response)


def collect_project(name):
    repo = api(f"/repos/{name}")
    if repo["private"] or repo["full_name"] != name:
        raise ValueError(f"Expected the configured public repository: {name}")
    releases = []
    # 有限分页；超过上限明确失败，不能将截断的下载量记为完整值。
    for page in range(1, 21):
        batch = api(f"/repos/{name}/releases?per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError(f"Invalid releases response: {name}")
        releases.extend(release for release in batch if not release["draft"])
        if len(batch) < 100:
            break
    else:
        raise ValueError(f"Release pagination limit exceeded: {name}")
    stable = [release for release in releases if not release["prerelease"]]
    latest = max(stable, key=lambda release: release["published_at"], default=None)
    result = {
        "repository": name,
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "open_issues_and_prs": repo["open_issues_count"],
        "published_release_count": len(releases),
        "release_asset_downloads": sum(
            asset["download_count"] for release in releases for asset in release["assets"]
        ),
        "latest_release": {
            "tag": latest["tag_name"], "published_at": latest["published_at"]
        } if latest else None,
    }
    for key in ("stars", "forks", "open_issues_and_prs", "published_release_count", "release_asset_downloads"):
        if type(result[key]) is not int or result[key] < 0:
            raise ValueError(f"Invalid metric {key}: {name}")
    return result


def main():
    now = datetime.now(ZONE)
    day = now.date().isoformat()
    target = Path("snapshots") / f"{day}.json"
    if target.exists():
        print(f"Already recorded {day}; no API requests or commits needed.")
        return
    # 所有请求成功后才落盘；API 失败不会用 0 代替缺失值。
    snapshot = {
        "schema_version": 1,
        "date": day,
        "observed_at": now.isoformat(timespec="seconds"),
        "projects": [collect_project(name) for name in PROJECTS],
    }
    count = daily_commit_count()
    projects = snapshot["projects"]
    target.parent.mkdir(exist_ok=True)
    for batch in range(1, count + 1):
        if datetime.now(ZONE).date().isoformat() != day:
            raise RuntimeError("Date changed during batch; abort without pushing.")
        snapshot["projects"] = projects[:batch * len(projects) // count]
        target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        subprocess.run(["git", "add", "--", str(target)], check=True)
        subprocess.run([
            "git", "commit", "-m", f"data: snapshot public projects for {day} ({batch}/{count})"
        ], check=True)
    print(f"Created {count} snapshot commits for {day}: {len(projects)} public projects.")


if __name__ == "__main__":
    main()
