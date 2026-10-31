from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.autorubric_export import PRODUCT_NAMES, export


REPO_ROOT = Path(__file__).resolve().parents[2]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_export_is_anonymized_and_group_split(tmp_path: Path) -> None:
    manifest = export(REPO_ROOT, tmp_path, "test-seed", holdout_per_task=2)
    dev = read_jsonl(tmp_path / "data" / "dev.jsonl")
    holdout = read_jsonl(tmp_path / "data" / "holdout.jsonl")

    assert manifest["signed_runs"] == 10
    assert manifest["cells"] == 40
    assert len(dev) == 24
    assert len(holdout) == 16
    assert {row["group_id"] for row in dev}.isdisjoint(
        {row["group_id"] for row in holdout}
    )
    assert all(row["group_id"].startswith("subject-") for row in dev + holdout)
    assert all("label_score" in row for row in dev)
    assert all("label_score" not in row for row in holdout)

    public_text = json.dumps(dev + holdout, ensure_ascii=False).lower()
    assert not any(product in public_text for product in PRODUCT_NAMES)
    assert "rationale" not in public_text


def test_export_rejects_a_holdout_that_consumes_all_runs(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot reserve"):
        export(REPO_ROOT, tmp_path, "test-seed", holdout_per_task=5)
