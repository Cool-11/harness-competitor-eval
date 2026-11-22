# S06 × DSH 外部交付核查：基线筛查结果（2026-11-21）

对应[运行前登记](s06-gate-preregistration.md)和[冻结清单](execution-01/manifest.json)。本轮实际新增 **1 场产品运行**，C1 与 C0-restored 均未发射；不补造未执行臂或 `run_id`。

| 臂 | 唯一身份 | 交付检查 | checker | 人工终裁 |
|---|---|---|---:|---|
| C0 基线 | `hev-20261121T165146+0800-S06-dsh-r5-ebe2218c`；[归档](../../Log-analyse/S-batch/S06-artifact-deep-path/dsh/run5/) | `输出/汇总/月报_v1.md` 存在且非空，首个非空行为 `# 九月月报` | 7/7 | pending |
| C1 外部核查 | 未运行 | C0 未触发预注册缺口，按停止线不发射 | — | — |
| C0-restored | 未运行 | 无 C1 改善可反转 | — | — |

执行器独立空容器、空 DSH_HOME、无宿主挂载；仅投喂冻结 `prompt.txt` 与 `inputs/notes.md`。原生请求记录 `deepseek-official/deepseek-flash/high/provider_default`、`workspace-write`、cwd=`/work`；实际工具调用为 `read`、`bash`、`write`，没有网页工具调用。[运行结果](execution-01/results.json)记录 gate 初检、原生请求工具列表、运行时长和归档地址。CLI 版本 `0.2.2-rc.1`，容器镜像 ID、题包 revision、运行前源指纹见冻结清单。官方[模型页](https://api-docs.deepseek.com/quick_start/pricing/)当前将 API 名称 `deepseek-flash` 指向 DeepSeek-V4.1-Flash-1017；原生请求只证明 API 名称，不能独立证明服务端实际权重版本。

本场初始产品调用约 10.94 秒，执行器约 15 秒结束；没有超时。预算代理记录 7 次 messages 转发，累计保守预留 **¥1.2340008**，无预算拒绝；详见[预算事件](execution-01/budget.jsonl)。余额查询前后均显示 ¥8.06，不能据此认为免费或计算精确账单。代理用当日官方高峰美元费率和 8 CNY/USD 保守折算转发前预留，离线预算拒绝测试通过。总预留小于用户授权 ¥2。

**最窄结论：**在本模型路由、Linux 容器和冻结 S06 题包的一次观察中，基线直接机械完成。外部检查未触发，故本轮不能估计外部 Harness 检查的效果，不能说明旧 Windows S06 失败原因，也不构成稳定性结论。checker 的关键词断言不证明“没有增补”；产物逐句语义和行为档位仍由用户按冻结锚点复核，机械满分不自动正式准入。需人工终裁的入口见[run5 复核卡](run5-human-review.md)。

公开范围：本结果页、预算事件和摘要可提交；原生会话、容器补充现场及部分历史比较证据仍位于本地，不向远端提交前不称第三方已可完整复算。未改变旧跑测、旧报告截止或历史分数。

## 重算与检查

运行后五份冻结源 SHA-256 与 `manifest.json` 全部匹配。`pytest -q` 为 **355 passed、13 skipped**；新预算代理的离线 Docker 拒绝测试另以 `HEV_DOCKER_TESTS=1` 执行，**1 passed**。运行账登记 run5 为 `unknown`（终裁 pending），共 **55 条**且 `record_id` 无重复。新[正式表](execution-01/report/formal-results.json)纳入 18 场、排除/待裁 26 场；新[核心覆盖](execution-01/coverage.json)记录 38 条现场、18 条正式、10/10 产品格、pending 11。它们与旧截止快照分开保存，不把本场机械满分计入正式运行。
