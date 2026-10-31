#!/usr/bin/env python3
"""Export signed behavior cells for a leakage-resistant AutoRubric pilot.

This script does not call a model and does not change official grades.  It turns
the signed S06/S11 behavior cells into anonymized development and holdout JSONL
files, keeping every run wholly on one side of the split.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASKS = ("S06-artifact-deep-path", "S11-corrupt-recovery")
PRODUCT_NAMES = ("codex", "doubao", "dsh", "workbuddy", "yuanbao")


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value[0:1] in {"'", '"'}:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value.strip("'\"")
    if value in {"true", "false"}:
        return value == "true"
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def parse_grade(path: Path) -> dict[str, Any]:
    """Parse the small, stable grade.yaml subset without a YAML dependency."""

    result: dict[str, Any] = {}
    cells: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_cells = False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line == "cells:":
            in_cells = True
            continue
        if in_cells and raw_line and not raw_line[0].isspace() and not raw_line.startswith("-"):
            if current:
                cells.append(current)
                current = None
            in_cells = False
        if in_cells:
            stripped = raw_line.lstrip()
            if stripped.startswith("- "):
                if current:
                    cells.append(current)
                current = {}
                key, value = stripped[2:].split(":", 1)
                current[key] = parse_scalar(value)
            elif current is not None and raw_line[0:1].isspace() and ":" in raw_line:
                key, value = stripped.split(":", 1)
                current[key] = parse_scalar(value)
            continue
        if raw_line and not raw_line[0].isspace() and ":" in raw_line:
            key, value = raw_line.split(":", 1)
            if key in {"run_id", "task", "product", "trial", "status"}:
                result[key] = parse_scalar(value)

    if current:
        cells.append(current)
    result["cells"] = cells
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def anonymous_subject(run_id: str, seed: str) -> str:
    token = hashlib.sha256(f"{seed}:{run_id}".encode("utf-8")).hexdigest()[:12]
    return f"subject-{token}"


def load_signed_runs(repo_root: Path) -> list[dict[str, Any]]:
    base = repo_root / "Log-analyse" / "S-batch"
    runs: list[dict[str, Any]] = []
    for task in TASKS:
        for grade_path in sorted((base / task).glob("*/run*/grade.yaml")):
            data = parse_grade(grade_path)
            if data.get("status") != "signed_off":
                continue
            if not data.get("cells"):
                continue
            data["_source"] = grade_path.relative_to(repo_root).as_posix()
            data["_source_sha256"] = sha256_file(grade_path)
            runs.append(data)
    return runs


def split_runs(
    runs: list[dict[str, Any]], seed: str, holdout_per_task: int
) -> dict[str, str]:
    split: dict[str, str] = {}
    by_task: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        by_task.setdefault(run["task"], []).append(run)

    for task, task_runs in by_task.items():
        ranked = sorted(
            task_runs,
            key=lambda item: hashlib.sha256(
                f"{seed}:{task}:{item['run_id']}".encode("utf-8")
            ).hexdigest(),
        )
        if len(ranked) <= holdout_per_task:
            raise ValueError(
                f"{task} only has {len(ranked)} signed runs; "
                f"cannot reserve {holdout_per_task} and retain development data"
            )
        for index, run in enumerate(ranked):
            split[run["run_id"]] = (
                "holdout" if index < holdout_per_task else "dev"
            )
    return split


def public_cell(
    run: dict[str, Any], cell: dict[str, Any], subject: str
) -> dict[str, Any]:
    evidence = str(cell.get("evidence", ""))
    for product in PRODUCT_NAMES:
        evidence = re.sub(re.escape(product), "<subject>", evidence, flags=re.IGNORECASE)
    return {
        "example_id": f"{subject}:{cell['id']}",
        "group_id": subject,
        "task_id": run["task"],
        "cell_id": cell["id"],
        "dimension": cell["dimension"],
        "criterion": cell["item"],
        "query": (
            "Use only the supplied observable evidence. Decide the 0-3 behavior "
            "tier for this criterion; if the evidence does not expose the behavior, "
            "abstain instead of inventing facts."
        ),
        "response": evidence,
        "label_score": cell["tier"],
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def export(
    repo_root: Path, out_dir: Path, seed: str, holdout_per_task: int
) -> dict[str, Any]:
    runs = load_signed_runs(repo_root)
    split = split_runs(runs, seed, holdout_per_task)
    public: dict[str, list[dict[str, Any]]] = {"dev": [], "holdout": []}
    audit_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []

    for run in sorted(runs, key=lambda item: (item["task"], item["run_id"])):
        subject = anonymous_subject(run["run_id"], seed)
        bucket = split[run["run_id"]]
        source_rows.append(
            {
                "subject": subject,
                "task_id": run["task"],
                "split": bucket,
                "source": run["_source"],
                "source_sha256": run["_source_sha256"],
            }
        )
        for cell in run["cells"]:
            row = public_cell(run, cell, subject)
            if bucket == "holdout":
                row.pop("label_score")
            public[bucket].append(row)
            audit_rows.append(
                {
                    "example_id": row["example_id"],
                    "human_tier": cell["tier"],
                    "human_rationale": cell.get("rationale", ""),
                    "source_sha256": run["_source_sha256"],
                    "split": bucket,
                }
            )

    write_jsonl(out_dir / "data" / "dev.jsonl", public["dev"])
    write_jsonl(out_dir / "data" / "holdout.jsonl", public["holdout"])
    write_jsonl(out_dir / "data" / "audit_labels.jsonl", audit_rows)
    write_jsonl(out_dir / "data" / "source_map.private.jsonl", source_rows)

    public_text = json.dumps(public, ensure_ascii=False).lower()
    leaked = [name for name in PRODUCT_NAMES if name in public_text]
    if leaked:
        raise ValueError(f"product-name leakage in public data: {leaked}")

    task_counts: dict[str, dict[str, int]] = {}
    for run in runs:
        task_counts.setdefault(run["task"], {"dev_runs": 0, "holdout_runs": 0})
        task_counts[run["task"]][f"{split[run['run_id']]}_runs"] += 1

    manifest = {
        "experiment_status": "discovery_only_not_for_official_scoring",
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "seed": seed,
        "split_unit": "whole_run",
        "holdout_per_task": holdout_per_task,
        "signed_runs": len(runs),
        "cells": sum(len(run["cells"]) for run in runs),
        "dev_cells": len(public["dev"]),
        "holdout_cells": len(public["holdout"]),
        "task_counts": task_counts,
        "limitations": [
            "Only two task families are represented.",
            "Cells from the same run are correlated even though no run crosses splits.",
            "Human labels inherit the current rubric and may contain rubric-specific bias.",
            "The sample is suitable for rubric discovery, not production validation.",
        ],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/autorubric/pilot-2026-10-30"),
    )
    parser.add_argument("--seed", default="autorubric-pilot-v1")
    parser.add_argument("--holdout-per-task", type=int, default=2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    out_dir = args.out if args.out.is_absolute() else repo_root / args.out
    manifest = export(repo_root, out_dir, args.seed, args.holdout_per_task)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
