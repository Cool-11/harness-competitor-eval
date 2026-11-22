# P0：隔离环境 S11 交付检查单变量筛查（2026-11-20，新运行前登记）

这是新 Linux 容器环境实验，不重启或改写 11 月 17 日已停止的污染场，也不把 Windows P2 阴性结果当作此处反事实。操作者为当前裁判 Agent；独立行为复评和终裁尚未发生。

用户在本次对话授权 `deepseek-official/deepseek-flash/high`、最多三场、每场总计600秒、累计费用不超过 **5元人民币**。首轮之后的同会话续接属于同一场，仍受600秒总限；不是三次HTTP请求上限。无额外模型或账号充值授权。

## 唯一干预与固定条件

对象为外部 Harness 的交付前检查组件，整体处理为“缺失文件检查 + 指明缺失文件 + 最多一次同session修复机会”。不是 DSH 官方内部插件，也不分别识别额外轮次、反馈文字的独立效应。基线 C0 与恢复 C0-restored 不进行追加提示；C1 才启用此组件，其他代码、容器镜像、任务、模型、预算和参数保持一致。

题包固定 `tasks/second_tasks/S11-corrupt-recovery/` 当前版本，启动前记录 task_revision；只向产品复制 prompt 正文与 inputs，不复制裁判文件、运行前元数据、旧产物或历史分数。每场新容器、新会话、新 `/work`；宿主接收目录绑定运行前记录，真实原生cwd为 `/work`，不伪装为Windows路径。使用新run16/17/18或启动时高于既有/预留序号的新连续槽位，恢复复用C0配置身份但运行身份不同。

DSH固定0.2.2-rc.1、headless、deepseek-official/deepseek-flash/high/provider_default、workspace-write、approval-policy never。同一公共patch关闭用户skills入口与遥测；每场全新空DSH_HOME，无跨场历史/记忆。`maxTokens=8192`是两臂共同的安全预算限制，不是处理变量；记录原生实际模型、推理、采样、工具与权限。Linux镜像与旧Windows不同，不做历史因果配对。

产品容器cap-drop ALL、no-new-privileges，无宿主目录或Docker socket挂载，仅连internal网络。唯一出网通道为另一容器的API预算代理，产品仅获得一次性代理nonce，不获得真实API key。代理只接受固定模型的Anthropic messages请求；不转发任意路径。真实API key仅经stdin进入代理内存，不进源码、argv、模型轨迹或入库文件。保留清洁镜像ID、Dockerfile、网络/挂载检查和容器ID。

费用以本轮实时核验的官方人民币高峰上界预留：Flash输入2元/百万token、输出8元/百万token；每个请求按完整UTF-8请求字节数+4096 framing token、请求max_tokens计算保守上界，转发前累计reserve不得超过5元，失败/超时也不退预留。输出大于8192、模型变化或其他API路径直接拒绝。结束读取实际CNY余额并另列变动，不把预留上界冒充账单金额。来源：[官方价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)，2026-11-20本机HTTP200读取核验。冻结费率仅适用于本次短筛查；未来重新核验。

## 终点与停止

主要机械终点：最终根目录 `result.md`、`error_report.md` 满足冻结S11 checker（0–7分），并保留逐项输出。完整任务成功还须语义/行为签认，不由checker自动宣布。次要记录初次交付、gate是否触发、工具恢复、模型请求、实际用量、保守费用、总时长及新增回归线索。

1. 先C0：若机械7/7，停止，报告新环境未复现漏交付；不为了出现失败继续抽样。
2. C0机械失败且证据有效，再C1：只有首轮正常结束且缺文件时，反馈题面要求的缺失文件名一次，使用同session；反馈不包含checker或真值。若首轮已全、gate未触发，停止且不归因。
3. 仅C1在gate实际触发后机械7/7，才C0-restored；否则保留阴性并停止。
4. 隔离、身份、cwd、实际模型/推理或工具条件变化，源漂移、API/预算失败均保留原件，停止后续槽位；明确是设施故障、unknown还是有效任务失败，人工裁定，不自动删除。费用到上限立即拒绝后续API转发，不追加试验。

每场先prepare，完成后collect。行为分、证据等级和终裁待人工按冻结锚点核验，初始adjudication=pending，不能冒充已正式准入或独立签署。三臂各最多一次，不报稳定性/因果差值区间。即使失败→成功→失败，也只是此配置下的机制筛查，需独立重复与等预算续接对照才能增强解释。它不构成完整指导的12场试点、双触发任务与负对照验收。
