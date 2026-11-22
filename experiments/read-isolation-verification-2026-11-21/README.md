# 读取隔离验证（2026-11-21）

> 目的：满足 [docs/41 第 23 行](../../docs/41-归因与研究轨道现行规则-2026-11-20.md) 的前置——发射付费产品场前，由隔离执行身份在同一启动环境验证裁判真值、历史产物及其他场均不可读取，并保留拒绝读取证据。

## 验证环境（同一启动环境）

| 项 | 值 |
|---|---|
| 镜像 | `harness-p0-dsh:20261120`（与 P0 DSH 隔离实验 run16/run17 同源，见 [p0_dsh_isolated.py](../../scripts/p0_dsh_isolated.py) `IMAGE`） |
| 启动参数 | `--network none --cap-drop ALL --security-opt no-new-privileges --pids-limit 128 --memory 2g --cpus 1` |
| 容器身份 | `uid=0`（容器内 root，非宿主 root）；`cwd=/work` |
| 裁判文件清单 | `AGENTS.md`、S11 `checker.py`/`spec.md`/`truth.json`、codex/run4 与 dsh/run6 的 `checker_output.txt`（历史产物与其他场） |

## 结果（全部通过）

| 检查项 | 结果 |
|---|---|
| 宿主挂载 | `mounts_count = 0`（无任何 `-v`/bind） |
| 特权 | `privileged = false` |
| 能力 | `CapDrop = [ALL]` |
| 网络 | `networks = none` |
| docker.sock | `/var/run/docker.sock` 不存在 |
| 禁止目录 | `/tests`、`/app`、`/logs`、`/root/.ssh` 均不存在 |
| 裁判文件读取 | 6 文件 × 5 路径变体 = 30 次尝试，全部 `denied_FileNotFoundError`（拒绝读取） |
| 文件系统搜索 | `/work` `/state` `/control` `/tmp` `/var/tmp` `/root` `/app` `/tests` 内未发现 `truth.json`/`checker.py`/`AGENTS.md` |
| 敏感环境变量 | 仅镜像自带 `GPG_KEY`（`A035...`），无真实密钥 |

## 结论

隔离执行身份在 `harness-p0-dsh:20261120` 隔离容器内**读不到**裁判真值、历史产物及其他场文件；容器无宿主挂载、非特权、丢弃全部 capability、无网络、无 docker.sock。读取隔离前置已通过，可作为后续付费产品场（任务1 的 baseline→change→recover 实验包）发射前的隔离依据。

## 证据

- [container-inspect.json](container-inspect.json)：`docker inspect` 原始输出（挂载/特权/能力/网络）。
- [read-isolation-result.json](read-isolation-result.json)：容器内读取拒绝证据（30 次 `FileNotFoundError` + marker 搜索）。
