#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_checkers.py — 元宝产物就位后的「一键产物分」管线

用途：
  当元宝产物（解压 yunbao.zip 后）按【规范题号】落到 <artifacts_root>/<题目录>/ 时，
  本脚本对 16 个用例逐一运行 cases/<题>/checker.py，原样汇总原始输出。

用法：
  python run_checkers.py <artifacts_root>                       # 打印到控制台
  python run_checkers.py <artifacts_root> --out checker_output.txt
  python run_checkers.py <artifacts_root> --selftest-first      # 先跑各 checker 负控制自测

约定：
  <artifacts_root>/ 下需存在与 cases/ 同名的规范题号子目录（见 CASES）。
  ⚠️ 同名产物（report.md×3、summary.md×2、summary.csv×2、assumptions.md×2）在平坦目录下
     会相互覆盖，务必先按内容归位到各题子目录，再运行本脚本。
"""
import argparse
import subprocess
import sys
from pathlib import Path

CASES = [
    "T00-hello-world", "T00b-file-format-probe", "T01-meeting-notes", "T02-data-cleaning",
    "T03-report-chain", "T04-long-doc-extract", "T05-contradiction-trap", "T06-corrupted-input-trap",
    "T07-privilege-trap", "T08-scope-constraint", "T09-ambiguity-assumptions", "T10-decision-log",
    "T11-artifact-location", "T12-cross-reference", "T13-proofreading", "T14-silent-anomaly-trap",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts_root", help="产物根目录（下含 16 个规范题号子目录）")
    ap.add_argument("--out", default="", help="把汇总原始输出写入的文件路径")
    ap.add_argument("--selftest-first", action="store_true", help="先跑各 checker 的负控制自测")
    a = ap.parse_args()

    here = Path(__file__).resolve().parent
    cases_root = (here / ".." / ".." / ".." / "cases").resolve()  # -> harness-competitor-eval/cases
    root = Path(a.artifacts_root).resolve()

    lines = []
    if a.selftest_first:
        lines.append("### checker 负控制自测（非产物分）")
        for c in CASES:
            r = subprocess.run([sys.executable, str(cases_root / c / "checker.py"), "--selftest"],
                               capture_output=True, text=True)
            lines.append(f"{c}: {r.stdout.strip()} (exit={r.returncode})")
        lines.append("")

    for c in CASES:
        d = root / c
        lines.append("=" * 64)
        lines.append(f"# ===== {c} =====")
        if not d.is_dir():
            lines.append(f"[SKIP] 缺目录 {d} —— 无产物")
            continue
        r = subprocess.run([sys.executable, str(cases_root / c / "checker.py"), str(d)],
                           capture_output=True, text=True)
        lines.append(r.stdout.rstrip())
        lines.append(f"(exit={r.returncode})")

    text = "\n".join(lines) + "\n"
    print(text)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"[saved] {a.out}")


if __name__ == "__main__":
    main()
