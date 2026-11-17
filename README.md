# Project Observatory · 个人开源项目观测

每天归档 LittleSixNine 的公开项目数据，观察项目关注度、版本发布和软件下载量的长期变化。每日快照是自动观测记录，不代表当天发生了代码开发。

## 最新快照

<!-- snapshot:start -->
观测时间：2026-11-18T01:13:34+08:00（北京时间）。括号为相较上次快照的增减。

| 项目 | Star | Fork | 未关闭 Issue/PR | Release 附件下载 | 最新正式版本 |
| --- | ---: | ---: | ---: | ---: | --- |
| [FrameMatter](https://github.com/LittleSixNine/FrameMatter) | 9 | 0 | 0 | 59 | build-3 |
| [PhotoTrail](https://github.com/LittleSixNine/PhotoTrail) | 55 | 4 | 0 | 142 | v0.5.17 |
| [FilmLog](https://github.com/LittleSixNine/FilmLog) | 0 | 0 | 0 | 2 | 暂无 |
| [Pawzz-video-downloader](https://github.com/LittleSixNine/Pawzz-video-downloader) | 0 | 0 | 0 | 5 | 暂无 |
| [photocut](https://github.com/LittleSixNine/photocut) | 0 | 0 | 0 | 0 | 暂无 |

[查看当日 JSON](snapshots/2026-11-18.json)
<!-- snapshot:end -->

## 观测范围与口径

固定观测 FrameMatter、PhotoTrail、FilmLog、Pawzz-video-downloader、photocut 五个公开项目，排除观测仓库自身及所有私有项目。新增观测对象需修改 `scripts/activity.py` 中的 `PROJECTS`。

- Star、Fork：GitHub 仓库接口返回的当前数量。
- 未关闭 Issue/PR：`open_issues_count`，包含未关闭的 Pull Request，并非仅 Issue。
- Release 附件下载：当前仍存在的所有已发布 Release（含预发布）的附件 `download_count` 之和，不含源码 ZIP/TAR 下载，不是独立用户数；删除附件或 Release 后可能下降。
- 最新正式版本：按 `published_at` 选最近发布的非草稿、非预发布 Release，不做版本号排序；没有正式 Release 时显示“暂无”。
- 每个日期保存一份 `snapshots/YYYY-MM-DD.json`，README 括号内比较上次已有快照，没有基准时只显示当前数值。各 API 请求先后执行，非同一瞬间的事务快照。

数据来源：[GitHub 仓库 API](https://docs.github.com/en/rest/repos/repos#get-a-repository)、[Release API](https://docs.github.com/en/rest/releases/releases#list-releases)。不抓取访客、克隆或其他需要跨仓库额外授权的数据。

## 自动执行与可靠性

北京时间（Asia/Shanghai，UTC+8）每天 **00:15** 主任务，**04:35、20:35** 补偿检查；cron 使用 UTC。每天首次成功采集后，用**一次提交**同时保存 JSON 和 README。即使数值没有变化，当天观测仍单独归档。同日后续触发直接跳过，不请求 API，也不新增提交。

API 超时、权限或格式错误会使任务失败，不写入虚构的零值或部分项目快照；下一次检查从远端重试。Release 查询有分页上限，达到上限明确失败。同一工作流串行运行，超时上限 5 分钟；没有 push 触发器，不递归，不无限重试。不回填历史，不修改提交日期。

运行使用内置 `GITHUB_TOKEN`，只声明本仓库的 `contents: write`；目标项目只读，不需要个人 Token 或第三方服务。提交作者为 LittleSixNine，邮箱为 `31497863+LittleSixNine@users.noreply.github.com`，提交进入默认分支。

## 手动运行、暂停与恢复

打开 [Actions 页面](https://github.com/LittleSixNine/project-observatory/actions/workflows/daily.yml)：

- 手动测试：**Run workflow**，选择默认分支。同日有快照时不会重复生成。
- 暂停：右上角 **… → Disable workflow**。
- 恢复：**Enable workflow**；需要立即采集时再点 **Run workflow**。

```sh
gh workflow disable daily.yml -R LittleSixNine/project-observatory
gh workflow enable daily.yml -R LittleSixNine/project-observatory
gh workflow run daily.yml -R LittleSixNine/project-observatory
```

GitHub 定时调度可能延迟或漏调度，无法绝对保证每天产生快照；长期无活动可能自动停用定时任务。整天失败会留下日期空缺，不用历史回填掩盖。项目转为私有、改名或被删除时，采集会失败，需调整观测列表。贡献是否展示及何时刷新以 GitHub 统计为准。

## 维护与历史

本项目于 2026-11-18 从 `daily-contributions` 自动活动日志改为真实项目数据观测；`activity.log` 为旧版日志，已停止更新，已有提交历史保留。正常自动任务每天最多一次数据提交，部署维护提交另计。

本地验证：在仓库根目录执行 `python3 tests/test_activity.py`（隔离仓库和模拟 API，不改真实项目）。脚本与测试沿用原路径，维护入口见 [项目索引](docs/INDEX.md)，变更见 [开发记录](docs/DEVLOG.md)。
