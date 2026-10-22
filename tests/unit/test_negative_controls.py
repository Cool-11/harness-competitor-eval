"""P1：负控制——空产物必须判 0，垃圾产物必须低于满分。"""

import pytest

from _util import case_id, parse_total, run_checker, scored_cases

CASES = scored_cases()


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_empty_artifacts_score_zero(case, tmp_path):
    art = tmp_path / "empty"
    art.mkdir()
    pr = run_checker(case, art)
    total = parse_total(pr.stdout)
    assert total is not None, f"{case.name} 无法解析合计行：{pr.stdout[-300:]}"
    assert total[0] == 0.0, f"{case.name} 空目录应判 0，实际 {total[0]}/{total[1]}"


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_garbage_artifacts_below_full(case, tmp_path):
    art = tmp_path / "garbage"
    art.mkdir()
    (art / "garbage.md").write_text("# lorem ipsum\n无关内容，不含题目要求。\n", encoding="utf-8")
    pr = run_checker(case, art)
    total = parse_total(pr.stdout)
    assert total is not None, f"{case.name} 无法解析合计行：{pr.stdout[-300:]}"
    assert total[0] < total[1], f"{case.name} 垃圾产物不应判满分：{total[0]}/{total[1]}"
