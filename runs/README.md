# runs/ 表现现场

每次运行一个记录包，命名规则：`runs/<题号>/<产品>/<运行序号>/`

```
runs/T05/yuanbao/run1/
├── timeline.md      # 执行时间线（模板见下）
├── session.log      # 终端/会话日志（CLI 类原始输出；GUI 类存导出的对话记录）
├── artifacts/       # 任务结束后整个工作目录快照
└── recording.txt    # 屏幕录像的网盘链接 + 时长 + 校验码
```

## timeline.md 模板

```markdown
# T05 × 元宝专家模式 × run1

| 时刻 | 阶段 | 我输入了什么 | 产品做了什么 | 可见输出 | 偏离/异常 | 证据引用 |
|---|---|---|---|---|---|---|
| 14:02 | 投喂 | 上传 inputs + 任务书原文 | 开始读取文件 | 显示已读 2 个文件 | - | rec 00:15 |
| 14:05 | 执行 | - | 输出部门统计表 | 产物含未提供的部门归属 | 疑似幻觉 | rec 02:10 / session.log L47 |
```

**证据引用**指向录屏时间戳（rec mm:ss）或日志行号——报告里任何一句关于本次运行的话都必须能点回这里。

---

## 目录已预建（别手敲）

全部运行目录由脚本生成：**16 用例 × 5 产品 = 100 个运行目录**（埋雷题 T05/06/07/14 每产品 2 个 run）。

```bash
python scripts/scaffold.py runs      # 幂等，已有文件不覆盖
```

每个运行目录预置三样：

```
runs/T05/yuanbao/run1/
├── artifacts/          # 空目录（含 .gitkeep，保证 git 能跟踪）
├── recording.txt       # 录屏链接 / 时长 / 校验码 模板
└── timeline.md         # 已填好元信息表头（含 prompt.txt 的 sha256 前 8 位）
```

## session.log 怎么来

| 产品类型 | 来源 |
|---|---|
| Codex / DSH（CLI） | 终端输出全选复制保存为 `session.log`；或运行时重定向：`... 2>&1 \| tee session.log` |
| Workbuddy / 元宝 / 豆包（GUI） | 产品内"导出对话记录"（文本/PDF）另存为 `session.log`；无导出功能则逐屏截图存 `session.log` 目录 |

## 录屏不进 git

`.gitignore` 已排除 `*.mp4/*.mkv/*.mov/*.webm`。录屏上传网盘后，把链接 + 时长 + 校验码写进 `recording.txt` 即可——**证据可指认，视频不必入库**。
