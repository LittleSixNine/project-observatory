"""隔离 Git 仓库及模拟 API，验证快照、失败保护和每日单次提交。"""

from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("activity", ROOT / "scripts/activity.py")
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)
README = (ROOT / "README.md").read_text(encoding="utf-8")


def release(tag="v1", count=10, prerelease=False, draft=False, published="2026-11-01T00:00:00Z"):
    return {"tag_name": tag, "published_at": published, "draft": draft,
            "prerelease": prerelease, "assets": [{"download_count": count}]}


class CollectionTests(unittest.TestCase):
    def test_pagination_totals_and_latest_stable(self):
        repo = {"full_name": "owner/repo", "private": False, "stargazers_count": 3,
                "forks_count": 2, "open_issues_count": 1}
        first = [release()] * 100
        last = [release("v2-beta", 5, prerelease=True, published="2026-11-02T00:00:00Z"),
                release("draft", 999, draft=True)]
        with patch.object(activity, "api", side_effect=[repo, first, last]) as api:
            result = activity.collect_project("owner/repo")
        self.assertEqual(result["release_asset_downloads"], 1005)
        self.assertEqual(result["published_release_count"], 101)
        self.assertEqual(result["latest_release"]["tag"], "v1")
        self.assertTrue(api.call_args.args[0].endswith("page=2"))

    def test_no_releases_and_private_rejection(self):
        repo = {"full_name": "owner/repo", "private": False, "stargazers_count": 0,
                "forks_count": 0, "open_issues_count": 0}
        with patch.object(activity, "api", side_effect=[repo, []]):
            result = activity.collect_project("owner/repo")
        self.assertIsNone(result["latest_release"])
        self.assertEqual(result["release_asset_downloads"], 0)
        with patch.object(activity, "api", return_value={**repo, "private": True}) as api:
            with self.assertRaises(ValueError):
                activity.collect_project("owner/repo")
            self.assertEqual(api.call_count, 1)

    def test_pagination_is_bounded(self):
        repo = {"full_name": "owner/repo", "private": False}
        with patch.object(activity, "api", side_effect=[repo] + [[release()] * 100] * 20) as api:
            with self.assertRaisesRegex(ValueError, "pagination limit"):
                activity.collect_project("owner/repo")
            self.assertEqual(api.call_count, 21)

class RecordingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.cwd = os.getcwd()
        os.chdir(self.temp.name)
        self.env = patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": os.devnull,
                                         "GIT_CONFIG_NOSYSTEM": "1", "TZ": "Asia/Shanghai"})
        self.env.start()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        Path("README.md").write_text(README, encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "test: initial")
        self.head = self.git("rev-parse", "HEAD")
        self.clock = patch.object(activity, "datetime")
        self.now = self.clock.start()
        self.now.now.return_value = datetime(2026, 11, 18, 1, 0, tzinfo=activity.ZONE)
        self.projects = [{"repository": name, "stars": 1, "forks": 0, "open_issues_and_prs": 0,
                          "published_release_count": 0, "release_asset_downloads": 0,
                          "latest_release": None} for name in activity.PROJECTS]

    def tearDown(self):
        self.clock.stop()
        self.env.stop()
        os.chdir(self.cwd)
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.STDOUT).strip()

    def test_one_commit_and_same_day_noop(self):
        with patch.object(activity, "collect_project", side_effect=self.projects):
            activity.main()
        snapshot = json.loads(Path("snapshots/2026-11-18.json").read_text())
        self.assertEqual(len(snapshot["projects"]), 5)
        self.assertEqual(self.git("rev-list", "--count", f"{self.head}..HEAD"), "1")
        self.assertEqual(set(self.git("diff", "--name-only", self.head, "HEAD").splitlines()),
                         {"snapshots/2026-11-18.json"})
        self.assertEqual(Path("README.md").read_text(encoding="utf-8"), README)
        self.assertTrue(self.git("log", "-1", "--format=%aI").endswith("+08:00"))
        head = self.git("rev-parse", "HEAD")
        with patch.object(activity, "collect_project") as collect:
            activity.main()
            collect.assert_not_called()
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_following_day_keeps_readme_and_archives_again(self):
        for day in (18, 19):
            self.now.now.return_value = datetime(2026, 11, day, 1, 0, tzinfo=activity.ZONE)
            with patch.object(activity, "collect_project", side_effect=self.projects):
                activity.main()
            self.assertEqual(Path("README.md").read_text(encoding="utf-8"), README)
            self.assertEqual(self.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"),
                             f"snapshots/2026-11-{day}.json")
        self.assertEqual(self.git("rev-list", "--count", f"{self.head}..HEAD"), "2")
        self.assertEqual(len(list(Path("snapshots").glob("*.json"))), 2)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_api_failure_writes_nothing(self):
        with patch.object(activity, "collect_project", side_effect=[{}, OSError("API unavailable")]):
            with self.assertRaises(OSError):
                activity.main()
        self.assertFalse(Path("snapshots").exists())
        self.assertEqual(Path("README.md").read_text(encoding="utf-8"), README)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.head)
        self.assertEqual(self.git("status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
