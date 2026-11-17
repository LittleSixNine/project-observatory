"""采集指定公开项目，每个北京时间日期保存一次真实观测。"""

from datetime import datetime
import html
import json
import os
from pathlib import Path
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
START = "<!-- snapshot:start -->"
END = "<!-- snapshot:end -->"


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


def metric(value, previous):
    return str(value) if previous is None else f"{value} ({value - previous:+d})"


def render(snapshot, previous):
    old = {project["repository"]: project for project in previous["projects"]} if previous else {}
    lines = [
        f"观测时间：{snapshot['observed_at']}（北京时间）。括号为相较上次快照的增减。",
        "",
        "| 项目 | Star | Fork | 未关闭 Issue/PR | Release 附件下载 | 最新正式版本 |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for project in snapshot["projects"]:
        name = project["repository"]
        baseline = old.get(name, {})
        values = [metric(project[key], baseline.get(key)) for key in (
            "stars", "forks", "open_issues_and_prs", "release_asset_downloads"
        )]
        release = project["latest_release"]
        tag = html.escape(release["tag"]).replace("|", "&#124;").replace("\n", " ") if release else "暂无"
        lines.append(f"| [{name.split('/')[-1]}](https://github.com/{name}) | " + " | ".join(values) + f" | {tag} |")
    lines.extend(["", f"[查看当日 JSON](snapshots/{snapshot['date']}.json)"])
    if previous:
        lines.append(f"比较基准：{previous['date']}（不一定是昨天）。")
    return "\n".join(lines)


def main():
    now = datetime.now(ZONE)
    day = now.date().isoformat()
    target = Path("snapshots") / f"{day}.json"
    if target.exists():
        print(f"Already recorded {day}; no API requests or commits needed.")
        return
    readme = Path("README.md").read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(START) > readme.index(END):
        raise ValueError("README must contain exactly one ordered snapshot marker pair")
    # 所有请求成功后才落盘；API 失败不会用 0 代替缺失值。
    snapshot = {
        "schema_version": 1,
        "date": day,
        "observed_at": now.isoformat(timespec="seconds"),
        "projects": [collect_project(name) for name in PROJECTS],
    }
    prior = sorted(path for path in target.parent.glob("*.json") if path.name < target.name)
    previous = json.loads(prior[-1].read_text(encoding="utf-8")) if prior else None
    updated = readme.split(START)[0] + START + "\n" + render(snapshot, previous) + "\n" + END + readme.split(END)[1]
    if datetime.now(ZONE).date().isoformat() != day:
        raise RuntimeError("Date changed during collection; abort without writing or pushing.")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path("README.md").write_text(updated, encoding="utf-8")
    subprocess.run(["git", "add", "--", str(target), "README.md"], check=True)
    subprocess.run(["git", "commit", "-m", f"data: snapshot public projects for {day}"], check=True)
    print(f"Created one snapshot commit for {day}: {len(PROJECTS)} public projects.")


if __name__ == "__main__":
    main()
