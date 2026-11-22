# S11 × DSH P2 运行前配置锁定（2026-11-17）

本页只记录本机 `dsh --profile headless --dump-config` 的摘要和目标字段，不保存可能含凭据的原始组合配置。以下哈希按 CLI 输出行用 `\n` 拼接后取 UTF-8 SHA-256；运行时仍要核对原生 `request/header`、工具列表与实际 cwd。

| 项 | 值 |
|---|---|
| CLI | `dsh --version = 0.2.2-rc.1` |
| 默认模型配置 | `deepseek-official / deepseek-flash`；实际路由以原生请求为准 |
| A1/A2 组合配置摘要 | `81fe079b765b88dbfa64376bfb26fcf82687e073b22e5c57b12d93c14a807e38` |
| B 组合配置摘要 | `f0376cce8d55be14db98ab63c8a870fabb4370ae328b7fe8aa0ff42c5934f69a` |
| B 补丁 SHA-256 | `5170a4a681868abcef242f3a0db45217c9b99c0ff5dc7268ddde6d2351a407f2` |
| 唯一配置字段差异 | A：`tool-pwsh.disabled = process.platform !== 'win32'`；B：`tool-pwsh.disabled = true`；其余输出差异为补丁来源注释 |
| 两臂共同工具 | `tool-fs` 保持装载，`tool-pwsh` 仅 A 臂在 Windows 装载 |
| 用户 skills 目录 | 顶层 24 项；排序后名称摘要 `d50fe4136e65c29c66451d2837728db33c1ea3c0f8a821bad8d3e0266f3b9ef1`，三臂运行前应复核不变；Skills 状态不冒称关闭 |

题包 SHA-256：`prompt.txt=41d608c42045fb2512489baf080aaa1d1cdd3452d4d0e946b7784f748fa88bb1`；`inputs/config.json=4583ff08648b54a173ecb733e52daff6d7721e3dce37feaab08aa29041d064b9`；`inputs/data.csv=fd668362c2f1e6151450be97d7a3d6c444f34275ec978d069dec7f227b037acc`；`checker.py=e2d80a7a72e1e51a198c0a757b12577cfc75cb6c8aff48320b0889fe2d2f200e`。

实验根目录固定为 `C:/tmp_s11_pwsh_channel_20261117`，三臂分别使用新 run10/run11/run12。该根在预检时不存在；历史归档的 S11 DSH 序号最高为 run9。三份计划在首次模型调用前同时写定，不在观察 A1 后修改 B/A2。每臂 600 秒；最多三次模型调用，若预注册停止线触发则少跑。
