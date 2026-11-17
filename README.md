# 每日自动活动日志

这是公开透明的 GitHub Actions 自动化实验。日志只代表自动任务运行，不代表实际项目开发成果。

## 工作原理

- 主任务每天北京时间（Asia/Shanghai，UTC+8）00:15 执行；04:35、20:35 再检查，补偿同一天的失败或漏调度。Workflow 中 cron 使用 UTC。
- 当天首次成功运行随机创建 1～5 次提交，每次向 `activity.log` 追加一条真实运行记录，整批推送到默认分支 `main`。同日后续检查或手动重试直接跳过。
- 同一工作流串行运行，最多运行 5 分钟；没有 push 触发器，不会递归。每次运行只尝试一次推送，失败由下一次定时检查或手动运行补偿。
- 提交使用执行时真实时间和北京时间偏移，不修改作者日期，不补填过去日期。失败批次如果没有推送，下一次从远端重新开始。
- 作者为 `LittleSixNine`，使用 `31497863+LittleSixNine@users.noreply.github.com` 隐私邮箱；运行仅使用内置 `GITHUB_TOKEN`，只声明 `contents: write`，不需要个人 Token 或额外服务。

## 手动运行、暂停与恢复

打开 [Actions 工作流页面](https://github.com/LittleSixNine/daily-contributions/actions/workflows/daily.yml)。

- 测试：点击 **Run workflow**，选择默认分支并运行。同日已经记录时不会增加提交。
- 暂停：右上角 **… → Disable workflow**。
- 恢复：点击 **Enable workflow**；如需立即执行，再点 **Run workflow**。恢复不会补写历史。

也可以使用 GitHub CLI：

```sh
gh workflow disable daily.yml -R LittleSixNine/daily-contributions
gh workflow enable daily.yml -R LittleSixNine/daily-contributions
gh workflow run daily.yml -R LittleSixNine/daily-contributions
```

## 限制与贡献统计

仓库是本人所有的公开独立仓库，提交进入默认分支，并使用账号对应的 GitHub noreply 邮箱，满足[官方贡献条件](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)。提交时区为北京时间，避免 UTC 日期错位；贡献图可能需要最多 24 小时刷新。

[GitHub 定时任务](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)可能延迟或丢弃，补偿任务也不保证一定运行。整天都失败会留下空缺，系统不会伪造历史来填补。公开仓库 60 天没有活动可能导致定时任务被禁用；正常的每日推送会持续产生活动，但长期故障后应检查工作流状态。账号限制、Actions 政策、分支保护或邮箱/用户名变更也可能影响运行或统计。

## 本地验证

在仓库根目录运行 `python3 tests/test_activity.py`，测试只在临时仓库内产生提交。

项目入口见 [docs/INDEX.md](docs/INDEX.md)，维护历史见 [docs/DEVLOG.md](docs/DEVLOG.md)。
