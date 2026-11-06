#!/usr/bin/env python3
"""Generate a small, auditable execution matrix from run.json files."""

import argparse
import datetime
import json
from pathlib import Path

try:
    from .sbatch import _eligibility
except ImportError:  # direct script execution
    from sbatch import _eligibility

REPO = Path(__file__).resolve().parent.parent
PRODUCTS = ("codex", "dsh", "workbuddy", "yuanbao", "doubao")
TASKS = ("S06-artifact-deep-path", "S11-corrupt-recovery")


def build(batch: Path) -> dict:
    cells = []
    for task in TASKS:
        for product in PRODUCTS:
            runs = []
            for path in sorted((batch / task / product).glob("run*/run.json")):
                doc = json.loads(path.read_text(encoding="utf-8"))
                eligible, reasons = _eligibility(doc)
                runs.append({
                    "run_id": doc.get("run_id", ""), "trial": doc.get("trial"),
                    "ruling": doc.get("adjudication", {}).get("final_ruling", "pending"),
                    "eligible": eligible, "reasons": reasons,
                    "task_revision": doc.get("binding", {}).get("task_revision", ""),
                    "product_revision": doc.get("binding", {}).get("product_revision", ""),
                    "artifact_score": doc.get("evaluation", {}).get("components", {}).get("artifact"),
                    "behavior_score": doc.get("evaluation", {}).get("components", {}).get("behavior"),
                    "evidence": path.as_posix(),
                })
            runs.sort(key=lambda item: item["trial"] if isinstance(item["trial"], int) else -1)
            cells.append({"task": task, "product": product, "runs": runs,
                          "eligible_runs": sum(r["eligible"] for r in runs)})
    all_runs = [r for cell in cells for r in cell["runs"]]
    return {
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": list(TASKS), "planned_cells": len(cells),
        "observed_run_records": len(all_runs),
        "formal_run_records": sum(r["eligible"] for r in all_runs),
        "formal_cells": sum(cell["eligible_runs"] > 0 for cell in cells),
        "cells": cells,
    }


def render(data: dict) -> str:
    lines = ["# 执行与覆盖快照", "", f"> 生成时间：{data['generated_at']}。仅统计 S11/S06 两题；每格目标为一款产品的一次新制式运行。旧场不追认。", "",
             f"目标格 **{data['planned_cells']}**；已有现场记录 **{data['observed_run_records']}** 条；正式准入 **{data['formal_run_records']}** 条，覆盖 **{data['formal_cells']}/{data['planned_cells']}** 格。记录数不等于独立有效样本数。", "",
             "| 题 | 产品 | 已归档 run | 正式准入 | 最新终裁 | 最新产物/行为 | 下一步 |", "|---|---|---:|---:|---|---|---|"]
    for cell in data["cells"]:
        runs = cell["runs"]
        latest = runs[-1] if runs else None
        next_step = "关键发现预注册重复" if cell["eligible_runs"] else "新场先 prepare，再核验 cwd/证据并终裁"
        score = (f"{latest['artifact_score'] if latest['artifact_score'] is not None else 'unknown'}/"
                 f"{latest['behavior_score'] if latest['behavior_score'] is not None else 'unknown'}"
                 if latest else "—")
        lines.append(f"| {cell['task']} | {cell['product']} | {len(runs)} | {cell['eligible_runs']} | {latest['ruling'] if latest else '未跑'} | {score} | {next_step} |")
    lines += ["", "## 运行身份与排除原因", ""]
    for cell in data["cells"]:
        for run in cell["runs"]:
            reason = "；".join(run["reasons"]) if run["reasons"] else "已准入"
            lines.append(f"- `{run['run_id']}` · {cell['task']}/{cell['product']} · {run['ruling']} · {reason} · `{run['evidence']}`")
    lines += ["", "**解释边界**：不同模型/产品形态分轨；n=1 只作该配置下观察。产物分与行为分分列，unknown 不折算为失败或满分。", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=Path, default=REPO / "Log-analyse" / "S-batch")
    args = ap.parse_args()
    data = build(args.batch)
    (args.batch / "coverage-status.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.batch / "coverage-status.md").write_text(render(data), encoding="utf-8")
    print(f"正式准入 {data['formal_run_records']} 条，覆盖 {data['formal_cells']}/{data['planned_cells']} 格")


if __name__ == "__main__":
    main()
