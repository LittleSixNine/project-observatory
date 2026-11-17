"""公开的自动活动日志；只使用执行时的真实日期。"""

from datetime import datetime
from pathlib import Path
import secrets
import subprocess
from zoneinfo import ZoneInfo


def main():
    day = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    log = Path("activity.log")
    previous = log.read_text(encoding="utf-8") if log.exists() else ""
    if any(line.startswith(day + " ") for line in previous.splitlines()):
        print(f"Already recorded {day}; no commits needed.")
        return

    count = secrets.randbelow(5) + 1
    for index in range(1, count + 1):
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        if now.date().isoformat() != day:
            raise RuntimeError("Date changed during batch; abort without pushing.")
        with log.open("a", encoding="utf-8") as stream:
            stream.write(f"{day} {now.isoformat(timespec='seconds')} automated activity {index}/{count}\n")
        subprocess.run(["git", "add", "--", "activity.log"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"chore: record daily activity {day} ({index}/{count})"],
            check=True,
        )
    print(f"Created {count} activity commits for {day}.")


if __name__ == "__main__":
    main()
