# 开发记录

## 2026-11-18

创建独立自动日志项目：每日主调度及两次补偿、随机 1～5 次实际日志提交、北京时间同日去重、串行执行及最小写权限；提供中文操作说明、维护入口和隔离仓库测试。

验证：隔离仓库测试及 Workflow YAML 检查通过。公开仓库默认分支为 main，Actions 已启用。首次手动运行 [44132266358](https://github.com/LittleSixNine/daily-contributions/actions/runs/44132266358) 成功生成 3 次日志提交并推送；GitHub API 将全部提交作者识别为 LittleSixNine，运行日志确认 Contents: write。仓库默认权限保持 read，不申请 PR 审批权限。发现旧版 checkout 的 Node.js 弃用提示，改用官方 v6 固定 SHA。

限制：尚未观察未来 cron 实际触发，贡献图存在刷新延迟；补偿不保证弥补整天停机，也不回填历史。

## 2026-11-18 · 改为公开项目观测

将仓库名称和用途改为 project-observatory，固定只读观测 FrameMatter、PhotoTrail、FilmLog、Pawzz-video-downloader、photocut 五个公开项目。沿用 scripts/activity.py 和测试入口，替换随机活动日志逻辑；每个北京时间日期仅用一次数据提交保存 JSON 快照并更新 README 差异表。保留旧 activity.log 和已有提交历史，不再追加旧日志；其他仓库不写入。

主要涉及采集脚本、隔离测试、Workflow、README 和项目索引；更新仓库名称守卫及运行时 API 令牌传递，仍只申请本仓库 contents: write，保留主调度和两次补偿。所有项目成功采集后才写入，API 失败不会被记为零值。公开指标口径、Release 分页上限、删包导致下载量下降及相较上次快照的含义已写入 README。

实际验证：6 项本地测试通过，覆盖发布分页及汇总、无版本与私有项目拒绝、分页上限、差异渲染、一次真实 Git 提交与同日去重、API 失败不落盘。未来 cron 调度可靠性仍不能保证，真实云端运行结果以 Actions 日志为准。

## 2026-11-18 · README 精简为英文单行

按要求将 README 改为一行英文项目说明。删除 scripts/activity.py 中全部 README 标记检查、历史差异表渲染和 README 读写逻辑；自动任务仅暂存并提交当天的 snapshots/YYYY-MM-DD.json，采集范围、数据格式、调度和同日去重不变。同步项目索引与回归测试。

实际验证：6 项测试通过，包含连续两个日期各归档一次且 README 字节内容不变、每次提交只包含当日 JSON、同日重试跳过，以及原有 API 汇总与失败保护检查；git diff --check 通过。测试中的未来日期仅用于临时仓库模拟，不向正式仓库写入未来快照。下一次真实日期的定时采集尚未观察。
