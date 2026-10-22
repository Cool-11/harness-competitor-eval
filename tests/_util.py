"""测试共享工具：题目发现、checker 调用、分数解析。"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TASKS = REPO / "tasks"
BATCHES = ("first_tasks", "second_tasks")
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# 校准题只探测产物形态，checker 明确"不计分"，没有合计行
NON_SCORING_IDS = {"T00b"}


def discover_cases():
    """扫描 tasks/{first_tasks,second_tasks}/ 下所有带 checker.py 的题目录。"""
    cases = []
    for batch in BATCHES:
        base = TASKS / batch
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir()):
            if d.is_dir() and (d / "checker.py").is_file():
                cases.append(d)
    return cases


def case_id(p: Path) -> str:
    return p.name.split("-")[0]


def scored_cases():
    """排除明确不计分的校准题。"""
    return [c for c in discover_cases() if case_id(c) not in NON_SCORING_IDS]


def run_checker(case_dir: Path, artifacts: Path):
    return subprocess.run(
        [sys.executable, str(case_dir / "checker.py"), str(artifacts)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def run_selftest(case_dir: Path):
    return subprocess.run(
        [sys.executable, str(case_dir / "checker.py"), "--selftest"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def parse_total(stdout: str):
    m = re.search(r"合计[：:]\s*([\d.]+)\s*/\s*([\d.]+)", stdout or "")
    return (float(m.group(1)), float(m.group(2))) if m else None
