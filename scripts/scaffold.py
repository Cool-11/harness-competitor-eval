"""
scaffold.py — 生成 ①每题独立的投喂用 prompt.txt ②Log-analyse/ 运行记录目录脚手架

用法：
  python scripts/scaffold.py prompt     # 只生成 prompt.txt
  python scripts/scaffold.py runs       # 只生成 Log-analyse/ 目录结构
  python scripts/scaffold.py all
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "tasks" / "first_tasks"
RUNS = ROOT / "Log-analyse"

PRODUCTS = ["codex", "workbuddy", "dsh", "yuanbao", "doubao"]
PRODUCT_CN = {"codex": "Codex", "workbuddy": "Workbuddy", "dsh": "DSH",
              "yuanbao": "元宝专家模式", "doubao": "豆包办公"}


def extract_instruction(task_md: str) -> str:
    """抽取 task.md 中「任务指令（原文，逐字投喂）」章节正文（去掉每行前缀 > 与空行）。"""
    if "## 任务指令" not in task_md:
        return ""
    seg = task_md.split("## 任务指令", 1)[1]
    # 截到下一个二级标题
    for stop in ("## 投喂说明", "## 完成条件", "## 维度映射", "## 运行次数", "## 投喂"):
        if stop in seg:
            seg = seg.split(stop, 1)[0]
    lines = []
    for ln in seg.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith(">"):
            s = s[1:].strip()
            if s.startswith("（") and s.endswith("）"):   # 模板占位说明
                continue
            lines.append(s)
    return "\n".join(lines).strip()


def gen_prompts():
    n = 0
    for d in sorted(CASES.glob("T*")):
        if d.name == "_template":
            continue
        t = d / "task.md"
        if not t.exists():
            continue
        instr = extract_instruction(t.read_text(encoding="utf-8"))
        if not instr:
            print(f"  ! {d.name}: 未抽取到任务指令")
            continue
        (d / "prompt.txt").write_text(
            instr + "\n",
            encoding="utf-8")
        h = hashlib.sha256((d / "prompt.txt").read_bytes()).hexdigest()[:8]
        print(f"  ✓ {d.name}/prompt.txt  ({len(instr)} 字符, sha256 前8位 {h})")
        n += 1
    print(f"共生成 {n} 个 prompt.txt")


def gen_runs():
    for d in sorted(CASES.glob("T*")):
        if d.name == "_template":
            continue
        tid = d.name
        tid_short = tid.split("-")[0]
        trap = any(k in tid for k in ("trap", "contradiction", "corrupted", "privilege", "silent"))
        runs_per = 2 if trap else 1
        task_hash = ""
        if (d / "prompt.txt").exists():
            task_hash = hashlib.sha256((d / "prompt.txt").read_bytes()).hexdigest()[:8]
        for prod in PRODUCTS:
            for i in range(1, runs_per + 1):
                rd = RUNS / tid_short / prod / f"run{i}"
                rd.mkdir(parents=True, exist_ok=True)
                (rd / "artifacts").mkdir(exist_ok=True)
                (rd / "shots").mkdir(exist_ok=True)
                (rd / "artifacts" / ".gitkeep").touch()
                tl = rd / "timeline.md"
                if not tl.exists():
                    tl.write_text(f"""# {tid_short} × {PRODUCT_CN[prod]} × run{i}

## 本次运行元信息

| 项 | 值 |
|---|---|
| 题号 / 产品 / 运行序号 | {tid_short} / {PRODUCT_CN[prod]} / run{i} |
| 日期与起止时刻 |  |
| 产品版本号 / 账号状态 |  |
| 任务书 sha256 前 8 位 | {task_hash} |
| 投喂方式 | 上传 inputs/ 全部文件 + 粘贴 prompt.txt 正文 |
| 墙钟耗时 |  |
| 澄清次数 |  |
| 新开会话 | ☐ 是（禁止在旧会话中追加） |

## 执行时间线

| 时刻 | 阶段 | 我输入了什么 | 产品做了什么 | 可见输出 | 偏离/异常 | 证据引用 |
|---|---|---|---|---|---|---|
|  | 投喂 | 上传 inputs + 粘贴任务指令 |  |  |  |  |
|  | 执行 |  |  |  |  |  |
|  | 结束 |  |  |  |  |  |

## 产物清单

| 文件名 | 落点路径 | 大小 | 是否任务书要求的产物 |
|---|---|---|---|
|  |  |  |  |
""", encoding="utf-8")
                (rd / "recording.txt").write_text(
                    "录屏链接：\n时长：\n校验码（如 md5）：\n", encoding="utf-8")
    total = sum(1 for _ in RUNS.glob("T*/*/run*/timeline.md"))
    print(f"Log-analyse/ 脚手架就绪：{total} 个运行记录目录")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("prompt", "all"):
        gen_prompts()
    if mode in ("runs", "all"):
        gen_runs()
