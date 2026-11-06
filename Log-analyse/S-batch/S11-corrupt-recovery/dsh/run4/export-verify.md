# DSH run4 用户导出日志核验

- 导出文件：`F:\for-project-tmp-run\runs\S11-corrupt-recovery\dsh\run4\log\dsh-session-session-517abe74-714f-42d4-8877-1235786dd407.zip`
- zip SHA-256：`240053C82820DAE163C4B31EE652F6B4F9BFE67EDDEA081E17F5CA3AB688FD57`
- zip 内 `session.v4.jsonl` SHA-256：`41AD847ED9A2EDB4A4B1503AC1CFBEC3091A40C0467D504BE5B79E230A657D00`
- 先前自动保存的 zstd SHA-256：`8BB8E2B3D39FF391A66D6CA429CA102B0BE6B9ECB06C1736CFF2E926F196BF97`
- 对照：自动保存版 69 条事件、导出版 71 条；共有的 seq 0–67 共 68 条 JSON 事件逐条相同。新增 seq 68/69 为 `command/run`、`command/done`，发生在 seq 67 `turn/end` 之后，属于导出操作。
- 会话头 cwd：`F:\for-project-tmp-run\runs\S11-corrupt-recovery\dsh\run4\work`；新导出未改变产品运行判断。

原始日志留在 F 盘，不直接上传 GitHub；仓库仅存哈希与核验记录。
