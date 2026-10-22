"""P0：fixture 分数快照——checker 改口径时这里必须显式变红。

快照文件：tests/regression/expected_scores.json
格式：{"S06": {"golden": 7.0, "partial": 5.5}, ...}
"""

import json
from pathlib import Path

import pytest

from _util import FIXTURES, case_id, discover_cases, parse_total, run_checker

SNAPSHOT = Path(__file__).resolve().parent / "expected_scores.json"
KINDS = ("golden", "partial")


def _cases():
    return {case_id(c): c for c in discover_cases()}


def _snapshot():
    if not SNAPSHOT.exists():
        return {}
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def _params():
    cases = _cases()
    for cid, kinds in sorted(_snapshot().items()):
        for kind in KINDS:
            if kind not in kinds:
                continue
            case = cases.get(cid)
            if case is None:
                continue
            yield pytest.param(case, FIXTURES / kind / case.name, float(kinds[kind]),
                               id=f"{cid}-{kind}")


@pytest.mark.parametrize("case,fixture,expected", list(_params()))
def test_fixture_score_matches_snapshot(case, fixture, expected):
    if not fixture.is_dir():
        pytest.skip(f"缺 fixture：{fixture.parent.name}/{fixture.name}")
    pr = run_checker(case, fixture)
    total = parse_total(pr.stdout)
    assert total is not None, f"{case.name} 无法解析合计行：{pr.stdout[-300:]}"
    assert total[0] == expected, (
        f"{case.name} {fixture.parent.name} 期望 {expected}，实际 {total[0]}/{total[1]}")


def test_snapshot_entries_have_fixtures():
    missing = []
    cases = _cases()
    for cid, kinds in _snapshot().items():
        for kind in KINDS:
            if kind in kinds and not (FIXTURES / kind / cases[cid].name).is_dir():
                missing.append(f"{kind}/{cases[cid].name}")
    assert not missing, f"快照有但 fixture 缺失：{missing}"


def test_every_fixture_is_in_snapshot():
    snapshot = _snapshot()
    extra = []
    for kind in KINDS:
        base = FIXTURES / kind
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir()):
            if not d.is_dir():
                continue
            cid = d.name.split("-")[0]
            if cid not in snapshot or kind not in snapshot[cid]:
                extra.append(f"{kind}/{d.name}")
    assert not extra, f"fixture 存在但快照缺条目：{extra}"
