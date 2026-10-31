import json
import sys

import pytest

from _util import REPO

sys.path.insert(0, str(REPO / "scripts"))
import eval_ledger  # noqa: E402


def test_six_accounts_have_distinct_ids(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ids = set()
    for record_type in eval_ledger.RECORD_TYPES:
        record = eval_ledger.register(
            record_type, f"subject-{record_type}", "passed",
            evidence=f"evidence/{record_type}.txt", path=path,
        )
        assert record["record_id"] not in ids
        ids.add(record["record_id"])
    assert eval_ledger.validate(path) == []
    assert len(eval_ledger.read_records(path)) == 6


def test_duplicate_id_is_rejected_by_validation(tmp_path):
    path = tmp_path / "ledger.jsonl"
    record = eval_ledger.register(
        "checker_selftest", "S11 --selftest", "passed",
        evidence="tests/regression/evidence/S11.txt", path=path,
    )
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    assert any("重复 record_id" in error for error in eval_ledger.validate(path))


def test_evidence_is_required(tmp_path):
    with pytest.raises(ValueError):
        eval_ledger.register(
            "offline_recompute", "S11 historical", "passed",
            evidence="", path=tmp_path / "ledger.jsonl",
        )


def test_sync_product_runs_is_idempotent(tmp_path):
    batch = tmp_path / "S-batch"
    run_dir = batch / "S11-corrupt-recovery" / "codex" / "run1"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(json.dumps({
        "schema_version": 2,
        "run_id": "hev-test-unique",
        "task": "S11-corrupt-recovery",
        "product": "codex",
        "trial": 1,
        "adjudication": {"final_ruling": "pending", "official_eligible": False},
    }), encoding="utf-8")
    ledger = tmp_path / "ledger.jsonl"
    assert eval_ledger.sync_product_runs(batch, ledger) == 1
    assert eval_ledger.sync_product_runs(batch, ledger) == 0
    records = eval_ledger.read_records(ledger)
    assert records[0]["record_type"] == "product_run"
    assert records[0]["related_run_id"] == "hev-test-unique"
