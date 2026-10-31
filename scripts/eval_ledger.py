#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""评测活动分账登记器。

产品运行由 sbatch.py 生成完整 run.json；其余活动用本脚本登记，避免把
checker 自测、离线复算、裸模型探针等误算成产品独立运行。
"""

import argparse
import datetime
import json
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "Log-analyse" / "evaluation-ledger.jsonl"
SUMMARY = REPO / "Log-analyse" / "evaluation-ledger.md"
SBATCH = REPO / "Log-analyse" / "S-batch"

RECORD_TYPES = {
    "product_run": "PR",
    "checker_selftest": "CS",
    "offline_recompute": "OR",
    "checker_regression": "CR",
    "bare_model_probe": "BM",
    "interface_precheck": "IP",
}
STATUSES = {"passed", "failed", "unknown", "invalid", "not_applicable"}


def _now() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def new_record_id(record_type: str) -> str:
    prefix = RECORD_TYPES[record_type]
    stamp = datetime.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8]}"


def read_records(path: Path = None) -> list[dict]:
    path = path or LEDGER
    if not path.is_file():
        return []
    records = []
    for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{no} 不是合法 JSON：{exc}") from exc
    return records


def register(record_type: str, subject: str, status: str, *,
             evidence: str, related_run_id: str = "", notes: str = "",
             metadata: dict = None, path: Path = None) -> dict:
    if record_type not in RECORD_TYPES:
        raise ValueError(f"未知 record_type：{record_type}")
    if status not in STATUSES:
        raise ValueError(f"未知 status：{status}")
    if not str(evidence).strip():
        raise ValueError("evidence 不得为空")
    path = path or LEDGER
    record = {
        "schema_version": 1,
        "record_id": new_record_id(record_type),
        "record_type": record_type,
        "subject": subject,
        "status": status,
        "recorded_at": _now(),
        "evidence": evidence,
        "related_run_id": related_run_id,
        "notes": notes,
        "metadata": metadata or {},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def validate(path: Path = None) -> list[str]:
    records = read_records(path)
    errors = []
    seen = set()
    required = {"record_id", "record_type", "subject", "status", "recorded_at", "evidence"}
    for index, record in enumerate(records, 1):
        missing = sorted(required - set(record))
        if missing:
            errors.append(f"第 {index} 行缺字段：{', '.join(missing)}")
        rid = record.get("record_id", "")
        if rid in seen:
            errors.append(f"重复 record_id：{rid}")
        seen.add(rid)
        if record.get("record_type") not in RECORD_TYPES:
            errors.append(f"{rid or index} record_type 非法")
        if record.get("status") not in STATUSES:
            errors.append(f"{rid or index} status 非法")
        if not str(record.get("evidence", "")).strip():
            errors.append(f"{rid or index} evidence 为空")
    return errors


def sync_product_runs(batch_root: Path = None, path: Path = None) -> int:
    """把 run.json 作为 product_run 引用登记；不复制、不改写原现场。"""
    batch_root = batch_root or SBATCH
    path = path or LEDGER
    records = read_records(path)
    existing = {
        r.get("related_run_id") for r in records
        if r.get("record_type") == "product_run" and r.get("related_run_id")
    }
    seen = set()
    added = 0
    for run_path in sorted(batch_root.glob("S*/**/run*/run.json")):
        doc = json.loads(run_path.read_text(encoding="utf-8"))
        run_id = doc.get("run_id", "")
        if not run_id:
            raise ValueError(f"run.json 缺 run_id：{run_path}")
        if run_id in seen:
            raise ValueError(f"产品现场 run_id 重复：{run_id}")
        seen.add(run_id)
        if run_id in existing:
            continue
        ruling = doc.get("adjudication", {}).get("final_ruling", "pending")
        status = {
            "pass": "passed", "fail": "failed", "invalid": "invalid",
            "not_applicable": "not_applicable",
        }.get(ruling, "unknown")
        rel = run_path.relative_to(REPO).as_posix() if run_path.is_relative_to(REPO) else str(run_path)
        register(
            "product_run",
            f"{doc.get('task', '')} / {doc.get('product', '')} / run{doc.get('trial', '')}",
            status,
            evidence=rel,
            related_run_id=run_id,
            notes="由 run.json 同步；最终比较资格仍以 sbatch formal-report 为准。",
            metadata={
                "official_eligible": doc.get("adjudication", {}).get("official_eligible", False),
                "legacy": doc.get("schema_version", 1) < 2,
            },
            path=path,
        )
        added += 1
    return added


def write_summary(path: Path = None, target: Path = None) -> None:
    records = read_records(path)
    target = target or SUMMARY
    counts = {name: 0 for name in RECORD_TYPES}
    for record in records:
        if record.get("record_type") in counts:
            counts[record["record_type"]] += 1
    lines = [
        "# 评测活动分账", "",
        "> 六类活动分别计数；只有 `product_run` 且通过正式准入终裁的记录可进入产品比较。", "",
        "| 类型 | 数量 |", "|---|---:|",
    ]
    for name in RECORD_TYPES:
        lines.append(f"| `{name}` | {counts[name]} |")
    lines += ["", "## 明细", "", "| record_id | 类型 | 对象 | 状态 | 证据 |", "|---|---|---|---|---|"]
    for record in records:
        lines.append(
            f"| {record.get('record_id', '')} | `{record.get('record_type', '')}` | "
            f"{record.get('subject', '')} | {record.get('status', '')} | {record.get('evidence', '')} |"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="六类评测活动分账登记")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("register")
    p1.add_argument("record_type", choices=sorted(RECORD_TYPES))
    p1.add_argument("subject")
    p1.add_argument("--status", required=True, choices=sorted(STATUSES))
    p1.add_argument("--evidence", required=True)
    p1.add_argument("--related-run-id", default="")
    p1.add_argument("--notes", default="")
    sub.add_parser("validate")
    sub.add_parser("summary")
    sub.add_parser("sync-products")
    args = ap.parse_args()
    if args.cmd == "register":
        record = register(
            args.record_type, args.subject, args.status,
            evidence=args.evidence, related_run_id=args.related_run_id, notes=args.notes,
        )
        print(record["record_id"])
    elif args.cmd == "validate":
        errors = validate()
        if errors:
            for error in errors:
                print(f"[错误] {error}")
            raise SystemExit(1)
        print(f"通过：{len(read_records())} 条记录，record_id 无重复。")
    elif args.cmd == "summary":
        write_summary()
        print(SUMMARY)
    else:
        added = sync_product_runs()
        print(f"新增 product_run 分账记录：{added}")


if __name__ == "__main__":
    main()
