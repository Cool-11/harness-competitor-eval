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
REPLACEMENTS = REPO / "benchmarks" / "core-run-replacements.json"


def _time(value: str) -> datetime.datetime | None:
    if not value:
        return None
    parsed = datetime.datetime.fromisoformat(value)
    # Legacy manifests have local timestamps without an offset; this project's
    # historical run records use Asia/Shanghai (UTC+08:00).
    return parsed if parsed.tzinfo else parsed.replace(
        tzinfo=datetime.timezone(datetime.timedelta(hours=8)))


def build(batch: Path, as_of: datetime.datetime | None = None,
          replacements: Path | None = None) -> dict:
    if as_of is not None and as_of.tzinfo is None:
        raise ValueError("as_of 必须带时区")
    cells = []
    undated = []
    for task in TASKS:
        for product in PRODUCTS:
            runs = []
            for path in sorted((batch / task / product).glob("run*/run.json")):
                doc = json.loads(path.read_text(encoding="utf-8"))
                manifest = path.parent / "manifest.json"
                meta = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
                observed_at = _time(meta.get("ended_at", "") or
                                    doc.get("adjudication", {}).get("adjudicated_at", ""))
                if as_of is not None and observed_at is None:
                    undated.append(path.as_posix())
                    continue
                if as_of is not None and observed_at > as_of:
                    continue
                adjudicated_at = _time(doc.get("adjudication", {}).get("adjudicated_at", ""))
                ruling = doc.get("adjudication", {}).get("final_ruling", "pending")
                if as_of is not None and (adjudicated_at is None or adjudicated_at > as_of):
                    ruling = "pending"
                    eligible, reasons = False, ["截止时尚未终裁"]
                else:
                    eligible, reasons = _eligibility(doc)
                runs.append({
                    "run_id": doc.get("run_id", ""), "trial": doc.get("trial"),
                    "ruling": ruling,
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
    ruling_counts = {status: sum(r["ruling"] == status for r in all_runs)
                     for status in ("pass", "fail", "invalid", "pending", "unknown", "not_applicable")}
    links_path = replacements if replacements is not None else REPLACEMENTS
    links = json.loads(links_path.read_text(encoding="utf-8")) if links_path.is_file() else []
    visible = {r["run_id"]: (cell["task"], cell["product"], r["trial"])
               for cell in cells for r in cell["runs"]}
    selected_links = []
    for link in links:
        source = visible.get(link["from_run_id"])
        target = visible.get(link["to_run_id"])
        if source and target:
            if source[:2] != target[:2] or source[2] >= target[2]:
                raise ValueError("替代场关联跨题/产品或运行序号倒退")
            selected_links.append(link)
    return {
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "as_of": as_of.isoformat() if as_of else "current_snapshot",
        "undated_excluded": undated,
        "scope": list(TASKS), "planned_cells": len(cells),
        "observed_run_records": len(all_runs),
        "formal_run_records": sum(r["eligible"] for r in all_runs),
        "formal_cells": sum(cell["eligible_runs"] > 0 for cell in cells),
        "ruling_counts": ruling_counts,
        "replacement_links": selected_links,
        "cells": cells,
    }


def render(data: dict) -> str:
    counts = data["ruling_counts"]
    lines = ["# 执行与覆盖快照", "", f"> 生成时间：{data['generated_at']}；截止：{data['as_of']}。仅统计 S11/S06 两题；每格目标为一款产品的一次新制式运行。旧场不追认。", "",
             "截止回放以 manifest.ended_at 为收件时间；缺 manifest 时以 adjudicated_at 作保守下界。旧版无时区时间按 Asia/Shanghai (+08:00) 解释；截止后才签署的场按 pending 计，不回填后来的终裁。当前快照反映文件现状。", "",
             f"目标格 **{data['planned_cells']}**；已有现场记录 **{data['observed_run_records']}** 条；正式准入 **{data['formal_run_records']}** 条，覆盖 **{data['formal_cells']}/{data['planned_cells']}** 格。记录数不等于独立有效样本数。", "",
             (f"终裁计数（按运行记录）：pass **{counts['pass']}**、fail **{counts['fail']}**、"
              f"invalid **{counts['invalid']}**、pending **{counts['pending']}**、"
              f"unknown **{counts['unknown']}**、not_applicable **{counts['not_applicable']}**。"
              "pass/fail 是结果终裁，正式准入另按门槛计算。"), "",
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
    lines += ["", "## 明确登记的原场→后续场", ""]
    for link in data["replacement_links"]:
        lines.append(f"- `{link['from_run_id']}` → `{link['to_run_id']}` · {link['evidence']}")
    if not data["replacement_links"]:
        lines.append("- 当前截止时点无已登记的双端运行。")
    if data["undated_excluded"]:
        lines += ["", "## 因缺时间戳未纳入截止统计", ""]
        lines.extend(f"- `{path}`" for path in data["undated_excluded"])
    lines += ["", "**解释边界**：不同模型/产品形态分轨；n=1 只作该配置下观察。产物分与行为分分列，unknown 不折算为失败或满分。", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=Path, default=REPO / "Log-analyse" / "S-batch")
    ap.add_argument("--as-of", help="ISO 截止时间，必须带时区；例如 2026-11-07T21:30:00+08:00")
    ap.add_argument("--output", type=Path, help="输出前缀；默认写到 batch/coverage-status")
    args = ap.parse_args()
    if args.as_of and datetime.datetime.fromisoformat(args.as_of).tzinfo is None:
        ap.error("--as-of 必须带时区偏移")
    data = build(args.batch, _time(args.as_of) if args.as_of else None)
    prefix = args.output or args.batch / "coverage-status"
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    prefix.with_suffix(".md").write_text(render(data), encoding="utf-8")
    print(f"正式准入 {data['formal_run_records']} 条，覆盖 {data['formal_cells']}/{data['planned_cells']} 格")


if __name__ == "__main__":
    main()
