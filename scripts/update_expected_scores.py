"""从 tests/fixtures 重新生成回归分数快照。

约束（生成时强制检查）：
- golden 必须等于满分
- partial 必须严格介于 0 和满分之间

用法：
  python scripts/update_expected_scores.py          # 写入快照
  python scripts/update_expected_scores.py --check  # 只校验，不写入（CI/本地检查用）
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TASKS = REPO / "tasks"
FIXTURES = REPO / "tests" / "fixtures"
SNAPSHOT = REPO / "tests" / "regression" / "expected_scores.json"
KINDS = ("golden", "partial")


def _case_dir(name: str):
    for batch in ("first_tasks", "second_tasks"):
        d = TASKS / batch / name
        if d.is_dir():
            return d
    return None


def _score(case_dir: Path, fixture: Path):
    pr = subprocess.run(
        [sys.executable, str(case_dir / "checker.py"), str(fixture)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    m = re.search(r"合计[：:]\s*([\d.]+)\s*/\s*([\d.]+)", pr.stdout or "")
    if not m:
        raise RuntimeError(f"{fixture} 无法解析合计行：{pr.stdout[-300:]}")
    return float(m.group(1)), float(m.group(2))


def build():
    snapshot = {}
    for kind in KINDS:
        base = FIXTURES / kind
        if not base.is_dir():
            continue
        for fixture in sorted(p for p in base.iterdir() if p.is_dir()):
            case_dir = _case_dir(fixture.name)
            if case_dir is None:
                raise RuntimeError(f"fixture 找不到对应题目：{kind}/{fixture.name}")
            got, full = _score(case_dir, fixture)
            cid = fixture.name.split("-")[0]
            snapshot.setdefault(cid, {})[kind] = got
            if kind == "golden" and got != full:
                raise RuntimeError(f"{fixture.name} golden 未得满分：{got}/{full}")
            if kind == "partial" and not (0 < got < full):
                raise RuntimeError(f"{fixture.name} partial 分数越界：{got}/{full}")
            print(f"{kind:8s} {fixture.name:28s} {got}/{full}")
    return dict(sorted(snapshot.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只比对，不写入")
    a = ap.parse_args()

    snapshot = build()
    text = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"

    if a.check:
        current = SNAPSHOT.read_text(encoding="utf-8") if SNAPSHOT.exists() else ""
        if current != text:
            print("快照与 fixture 实际分数不一致，请运行不带 --check 的命令更新", file=sys.stderr)
            sys.exit(1)
        print("快照一致")
        return

    SNAPSHOT.write_text(text, encoding="utf-8")
    print(f"已写入 {SNAPSHOT}（{len(snapshot)} 题）")


if __name__ == "__main__":
    main()
