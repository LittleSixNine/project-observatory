# 项目索引

- `../README.md`：一行英文项目说明，不由自动任务更新。
- `../.github/workflows/daily.yml`：定时、手动触发、最小权限及推送。
- `../scripts/activity.py`：公开项目 API 采集、JSON 快照和每天一次提交；只提交当日 JSON。
- `../tests/test_activity.py`：分页、统计口径、失败保护和隔离 Git 仓库内的提交验证。
- `../snapshots/`：按北京时间日期保存的公开项目观测数据，由工作流生成。
- `../activity.log`：旧版自动活动日志，停止更新并保留历史。
- `DEVLOG.md`：维护记录。
