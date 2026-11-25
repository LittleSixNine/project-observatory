# 项目索引

通过 GitHub Actions 每日归档五个个人公开项目的指标，数据保存在 `snapshots/YYYY-MM-DD.json`，不更新 README。

每日按日期固定伪随机抽取 0～5 批提交，采用均值 2.5、标准差 1 的截断离散正态分布：0～5 次的概率约为 2.1%、13.6%、34.2%、34.2%、13.6%、2.1%。同日重试保持相同目标，不会重新抽样。

抽到 0 次当天不采集、不生成快照，也不补填该日期。其余日期完整采集一次，按项目分批提交后一次性推送，最终快照包含全部五个项目；同日成功后不再采集或提交。中间提交仅包含已加入的项目，使用数据时应读取默认分支的最终快照。

- `../README.md`：一行英文项目说明。
- `../.github/workflows/daily.yml`：北京时间 00:15 主任务、04:35 和 20:35 补偿检查；支持手动运行。
- `../scripts/activity.py`：项目列表、API 采集、JSON 归档和同日去重。
- `../tests/test_activity.py`：采集口径、失败保护、每日提交及 README 不变的验证。
- `../snapshots/`：按日期保存的真实观测数据，不回填历史。
- `../activity.log`：已停止更新的旧版日志。
- `DEVLOG.md`：维护与验证记录。

在 Actions 工作流页面使用 **Run workflow** 手动执行、**Disable workflow** 暂停、**Enable workflow** 恢复。本地检查命令：`python3 tests/test_activity.py`。
