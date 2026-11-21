"""Recompute core checker boundaries; semantic expectations are unsigned review aids."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def calibrate(repo: Path = REPO) -> dict:
    results = []
    contracts = {}
    for task in ("S06-artifact-deep-path", "S11-corrupt-recovery"):
        checker = repo / "tasks/second_tasks" / task / "checker.py"
        contract_files = [checker.parent / name for name in ('prompt.txt', 'spec.md', 'truth.json', 'checker.py')]
        contract_files += [path for path in (checker.parent / 'inputs').rglob('*') if path.is_file()]
        contracts[task] = {path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in contract_files}
        spec = importlib.util.spec_from_file_location("calibration_checker", checker)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for variant in ("golden", "partial", "tampered"):
            fixture = repo / "tests/fixtures" / variant / task
            if fixture.is_dir():
                results.append({"task": task, "case": variant,
                                "checker_score": module.check(fixture)[1],
                                "fixture": fixture.relative_to(repo).as_posix(),
                                "fixture_sha256": {path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                                                   for path in fixture.rglob('*') if path.is_file()},
                                "checker_sha256": hashlib.sha256(checker.read_bytes()).hexdigest()})
        if task.startswith("S06"):
            golden = (repo / "tests/fixtures/golden" / task / "输出/汇总/月报_v1.md").read_text(encoding="utf-8")
            cases = [
                ("unsupported_addition", golden + "\n- 本月营收翻倍。\n", "reject: 无依据增补"),
                ("keywords_only", "# 九月月报\n\nv0.3、8 秒、2 秒、6 人、供应商 B、移动端适配。\n", "reject: 未列原材料事项"),
                ("omission", golden.replace("- 遗留：移动端适配尚未启动\n", ""), "reject: 遗漏"),
                ("equivalent", golden.replace("降到 2 秒", "缩短至 2 秒"), "accept: 等价改写"),
            ]
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = root / "输出/汇总/月报_v1.md"
                target.parent.mkdir(parents=True)
                for name, content, expectation in cases:
                    target.write_text(content, encoding="utf-8")
                    results.append({"task": task, "case": name,
                                    "checker_score": module.check(root)[1],
                                    "sample_text": content, "semantic_expectation_draft": expectation,
                                    "checker_sha256": hashlib.sha256(checker.read_bytes()).hexdigest()})
    return {"version": 2, "status": "local_calibration_not_official_rescoring", "task_contracts": contracts,
            "independent_review": "pending", "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output exists; choose a new calibration identity")
    result = calibrate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in result['results']:
        print(row['task'], row['case'], row['checker_score'])


if __name__ == "__main__":
    main()
