# 项目索引

通过 GitHub Actions 每日归档五个个人公开项目的指标，数据保存在 `snapshots/YYYY-MM-DD.json`。正常任务每天最多一次数据提交，不更新 README。

- `../README.md`：一行英文项目说明。
- `../.github/workflows/daily.yml`：北京时间 00:15 主任务、04:35 和 20:35 补偿检查；支持手动运行。
- `../scripts/activity.py`：项目列表、API 采集、JSON 归档和同日去重。
- `../tests/test_activity.py`：采集口径、失败保护、每日提交及 README 不变的验证。
- `../snapshots/`：按日期保存的真实观测数据，不回填历史。
- `../activity.log`：已停止更新的旧版日志。
- `DEVLOG.md`：维护与验证记录。

在 Actions 工作流页面使用 **Run workflow** 手动执行、**Disable workflow** 暂停、**Enable workflow** 恢复。本地检查命令：`python3 tests/test_activity.py`。
