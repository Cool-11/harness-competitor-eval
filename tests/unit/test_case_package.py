"""P1：题包完整性 + checker 自测。自动覆盖 tasks/ 下全部题目。"""

import json

import pytest

from _util import case_id, discover_cases, run_selftest

CASES = discover_cases()


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_required_files_exist(case):
    for name in ("task.md", "prompt.txt", "checker.py", "spec.md"):
        assert (case / name).is_file(), f"{case.name} 缺 {name}"
    assert (case / "prompt.txt").read_text(encoding="utf-8").strip(), f"{case.name} prompt.txt 为空"


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_truth_json_parses(case):
    truth = case / "truth.json"
    if not truth.exists():
        pytest.skip("无 truth.json（设计如此）")
    data = json.loads(truth.read_text(encoding="utf-8"))
    assert data, f"{case.name} truth.json 为空"


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_checker_selftest_passes(case):
    pr = run_selftest(case)
    assert pr.returncode == 0, f"{case.name} --selftest 失败：\n{pr.stdout[-800:]}\n{pr.stderr[-400:]}"
