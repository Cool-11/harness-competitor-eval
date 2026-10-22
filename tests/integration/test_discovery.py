"""P1：题库发现契约——新增题目自动纳入测试，题号不得重复。"""

from _util import BATCHES, TASKS, case_id, discover_cases

CASES = discover_cases()


def test_all_batches_present():
    for batch in BATCHES:
        assert (TASKS / batch).is_dir(), f"缺批次目录 tasks/{batch}"


def test_case_count_is_at_least_51():
    assert len(CASES) >= 51, f"只发现 {len(CASES)} 个题目录，预期 ≥51"


def test_case_ids_unique():
    ids = [case_id(c) for c in CASES]
    assert len(ids) == len(set(ids)), f"题号重复：{sorted(i for i in ids if ids.count(i) > 1)}"


def test_each_case_has_checker():
    for case in CASES:
        assert (case / "checker.py").is_file(), f"{case.name} 缺 checker.py"
