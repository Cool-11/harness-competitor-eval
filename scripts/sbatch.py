#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sbatch.py — S 批（压力层）跑测脚手架

职责：把"准备一次运行 → 跑完归档 → 自动判分 → 记入结果大表"标准化，减少人为漂移。
真值/checker/prompt 的纪律见 docs/03-打分细则-v1.md（已冻结）与 docs/10。

用法：
  # 1) 准备：建工作目录、放入该题 inputs、打印投喂指令位置与哈希
  python scripts/sbatch.py prepare S06 dsh --run 1

  # 2) 跑：按 docs/05 手册，把 prompt.txt 全文粘贴给产品（新开会话），录屏/日志留痕

  # 3) 归档+判分：快照工作目录 → 跑 checker → 写结果行 + 三件套证据包
  python scripts/sbatch.py collect S06 dsh --run 1 --work "F:\\runs_tmp\\S06\\dsh\\run1\\work" --interventions 0 --turns 6
"""

import argparse
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CASES = REPO / "tasks" / "second_tasks"
SBATCH = REPO / "Log-analyse" / "S-batch"
TMP_ROOT = Path(r"F:\runs_tmp")
PRODUCTS = ["codex", "dsh", "workbuddy", "yuanbao", "doubao"]


def _sha8(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:8]


def _write_json(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _num(v: str):
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


def _resolve(name: str):
    """把短 id（如 S06）解析到真实用例目录（如 S06-artifact-deep-path）。"""
    d = CASES / name
    if d.is_dir():
        return d
    cands = sorted(p for p in CASES.iterdir()
                   if p.is_dir() and p.name.startswith(name + "-"))
    return cands[0] if cands else None


def prepare(case: str, product: str, run: int) -> int:
    cdir = _resolve(case)
    if cdir is None:
        print(f"[错误] 找不到用例目录：{CASES}\\{case}*")
        return 2
    if not (cdir / "prompt.txt").is_file():
        print(f"[错误] 缺 prompt.txt：{cdir}")
        return 2

    work = TMP_ROOT / cdir.name / product / f"run{run}" / "work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)

    src = cdir / "inputs"
    n = 0
    if src.is_dir():
        for f in src.rglob("*"):
            if f.is_file():
                dst = work / f.relative_to(src)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)
                n += 1

    prompt = cdir / "prompt.txt"
    prep = {
        "case": cdir.name,
        "product": product,
        "run": run,
        "started_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "prompt_sha8": _sha8(prompt),
        "inputs_sha8": {
            str(f.relative_to(src)): _sha8(f)
            for f in src.rglob("*") if f.is_file()
        } if src.is_dir() else {},
    }
    _write_json(work.parent / "prepare.json", prep)
    print(f"工作目录已就绪：{work}（放入 {n} 个输入文件）")
    print(f"投喂指令：{prompt}  ｜ sha256[:8] = {_sha8(prompt)}")
    print(f"→ 新开 {product} 会话，把 prompt.txt 全文粘贴投喂；录屏 / 日志留痕。")
    print(f"→ 跑完后：python scripts/sbatch.py collect {case} {product} --run {run} --work \"{work}\"")
    return 0


def collect(case: str, product: str, run: int, work: str,
            interventions: int = 0, turns: int = 0,
            elapsed=None, timed_out: bool = False, rerun: bool = False) -> int:
    cdir = _resolve(case)
    if cdir is None:
        print(f"[错误] 找不到用例目录：{CASES}\\{case}*")
        return 2
    chk = cdir / "checker.py"
    if not chk.is_file():
        print(f"[错误] 缺 checker.py：{chk}")
        return 2

    w = Path(work)
    if not w.is_dir():
        print(f"[错误] 工作目录不存在：{w}")
        return 2

    out = SBATCH / cdir.name / product / f"run{run}"
    art = out / "artifacts"
    if art.exists():
        shutil.rmtree(art)
    art.mkdir(parents=True, exist_ok=True)
    for f in w.rglob("*"):
        if f.is_file():
            dst = art / f.relative_to(w)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
    n_art = sum(1 for f in art.rglob("*") if f.is_file())

    pr = subprocess.run([sys.executable, str(chk), str(art)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    (out / "checker_output.txt").write_text(pr.stdout or "", encoding="utf-8")

    m = re.search(r"合计[：:]\s*([\d.]+)\s*/\s*([\d.]+)", pr.stdout or "")
    got, full = (m.group(1), m.group(2)) if m else ("?", "?")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    metrics = {}
    mm = re.search(r"METRICS_JSON:\s*(\{.*\})\s*$", pr.stdout or "", re.MULTILINE)
    if mm:
        try:
            metrics = json.loads(mm.group(1))
        except json.JSONDecodeError:
            metrics = {}

    prep_path = w.parent / "prepare.json"
    prep = json.loads(prep_path.read_text(encoding="utf-8")) if prep_path.is_file() else {}
    started_at = prep.get("started_at") or now
    ended_at = datetime.datetime.now().isoformat(timespec="seconds")
    if elapsed is None:
        try:
            elapsed = (datetime.datetime.now()
                       - datetime.datetime.fromisoformat(started_at)).total_seconds()
        except (TypeError, ValueError):
            elapsed = None

    _write_json(out / "manifest.json", {
        "case": cdir.name,
        "product": product,
        "run": run,
        "started_at": started_at,
        "ended_at": ended_at,
        "prompt_sha8": prep.get("prompt_sha8") or _sha8(cdir / "prompt.txt"),
        "inputs_sha8": prep.get("inputs_sha8", {}),
        "artifacts_count": n_art,
        "checker_exit": pr.returncode,
        "interventions": interventions,
        "rerun": rerun,
    })
    _write_json(out / "usage.json", {
        "elapsed_seconds": round(elapsed, 1) if elapsed is not None else None,
        "turns": turns,
        "timed_out": timed_out,
        "manual_interventions": interventions,
    })
    _write_json(out / "score.json", {
        "raw_got": _num(got),
        "raw_full": _num(full),
        "metrics": metrics,
        "failure_code": "",
        "evidence_grade": "",
        "status": "timeout" if timed_out else "graded",
    })

    SBATCH.mkdir(parents=True, exist_ok=True)
    res = SBATCH / "results.md"
    if not res.exists():
        res.write_text(
            "# S 批跑测结果大表\n\n"
            "> 产物分 = checker 原始实得/满分；**归一分**按 `docs/03 §1.8`：`实得/满分 × 权重`"
            "（普通题 6、埋雷题 4）。行为分 0–3 人工按 `spec.md` 锚点另判，逐条写证据引用。\n"
            "> 失败编码按 `docs/10` 两轴 `A_-B_`。\n\n"
            "| 题 | 产品 | run | 产物分(实得/满分) | 归一分 | checker exit | 跑测时间 | 备注 |\n"
            "|---|---|---|---|---|---|---|---|\n",
            encoding="utf-8")

    row = f"| {cdir.name} | {product} | {run} | {got}/{full} | | exit={pr.returncode} | {now} | |\n"
    res.write_text(res.read_text(encoding="utf-8") + row, encoding="utf-8")

    print(f"产物已归档：{art}")
    print(f"checker 输出：{out / 'checker_output.txt'}")
    print(f"证据三件套：manifest.json / usage.json / score.json → {out}")
    print(f"产物分：{got}/{full}（exit={pr.returncode}）→ 已记入 {res}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="S 批跑测脚手架")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("prepare", help="准备一次运行（建工作目录、放 inputs）")
    p1.add_argument("case")
    p1.add_argument("product", choices=PRODUCTS)
    p1.add_argument("--run", type=int, default=1)

    p2 = sub.add_parser("collect", help="归档产物并判分，写入结果表与证据三件套")
    p2.add_argument("case")
    p2.add_argument("product", choices=PRODUCTS)
    p2.add_argument("--run", type=int, default=1)
    p2.add_argument("--work", required=True)
    p2.add_argument("--interventions", type=int, default=0, help="人工干预次数")
    p2.add_argument("--turns", type=int, default=0, help="会话轮次")
    p2.add_argument("--elapsed", type=float, default=None, help="墙钟秒数；缺省按 prepare 时间戳推算")
    p2.add_argument("--timed-out", action="store_true", help="超时终止（二值失败事件）")
    p2.add_argument("--rerun", action="store_true", help="是否为重跑")

    a = ap.parse_args()
    if a.cmd == "prepare":
        sys.exit(prepare(a.case, a.product, a.run))
    else:
        sys.exit(collect(a.case, a.product, a.run, a.work,
                         interventions=a.interventions, turns=a.turns,
                         elapsed=a.elapsed, timed_out=a.timed_out, rerun=a.rerun))


if __name__ == "__main__":
    main()
