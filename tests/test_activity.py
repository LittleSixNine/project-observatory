"""在隔离仓库中验证真实提交、文件修改、日期和同日重试。"""

from datetime import datetime
import os
from pathlib import Path
import subprocess
import tempfile
from zoneinfo import ZoneInfo

script = Path(__file__).resolve().parents[1] / "scripts/activity.py"
with tempfile.TemporaryDirectory() as directory:
    env = {**os.environ, "TZ": "Asia/Shanghai"}
    # 不继承机器的签名设置、模板或 hooks。
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

    def run(*args):
        return subprocess.check_output(args, cwd=directory, env=env, text=True).strip()

    run("git", "init", "-b", "main")
    run("git", "config", "user.name", "Test")
    run("git", "config", "user.email", "test@example.com")
    run("python3", str(script))
    lines = (Path(directory) / "activity.log").read_text().splitlines()
    count = int(run("git", "rev-list", "--count", "HEAD"))
    assert 1 <= count <= 5 and len(lines) == count
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    assert all(line.startswith(today + " ") for line in lines)
    assert run("git", "log", "-1", "--format=%aI").endswith("+08:00")
    for sha in run("git", "rev-list", "HEAD").splitlines():
        assert "activity.log" in run("git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", sha)
    head = run("git", "rev-parse", "HEAD")
    assert "Already recorded" in run("python3", str(script))
    assert run("git", "rev-parse", "HEAD") == head
    assert not run("git", "status", "--porcelain")
print("PASS: 1–5 real commits, +08:00 author date, same-day retry is a no-op.")
