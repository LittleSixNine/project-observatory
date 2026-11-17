# 项目维护

本项目只记录透明的自动化活动，不得描述为人工开发成果。不得回填或伪造历史提交日期，不引入个人 Token，不修改其他仓库。

- 修改调度、身份或补偿机制：先读 README.md 和 .github/workflows/daily.yml。
- 修改日志生成：先读 scripts/activity.py 和 tests/test_activity.py。
- 按任务入口读取，发现依赖再扩大范围。行为变化同步 README；文件或职责变化同步 [索引](docs/INDEX.md)。
- 每项持久修改任务交付前合并追加一条 [开发记录](docs/DEVLOG.md)，注明日期、原因、涉及位置、实际验证及遗留问题。只读检查不记账，不递归记录文档维护本身。
