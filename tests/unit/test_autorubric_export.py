from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts.autorubric_export import PRODUCT_NAMES, export, load_signed_runs


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


def copy_frozen_sources(root: Path) -> list[dict]:
    relative = Path("experiments/autorubric/pilot-2026-10-30")
    shutil.copytree(REPO_ROOT / relative, root / relative)
    entries = json.loads((root / relative / "sources.json").read_text())['sources']
    for entry in entries:
        target = root / entry['source']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / entry['source'], target)
    return entries


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_frozen_grades_survive_checkout_newlines(tmp_path: Path, newline: bytes) -> None:
    entries = copy_frozen_sources(tmp_path)
    for entry in entries:
        path = tmp_path / entry['source']
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", newline))
    actual = load_signed_runs(tmp_path)
    assert actual == load_signed_runs(REPO_ROOT)


@pytest.mark.parametrize("target", ["source", "snapshot", "missing_snapshot"])
def test_frozen_grades_reject_content_drift(tmp_path: Path, target: str) -> None:
    entry = copy_frozen_sources(tmp_path)[0]
    snapshot = tmp_path / "experiments/autorubric/pilot-2026-10-30/snapshots-v1" / f"{entry['sha256']}.bin"
    if target == "missing_snapshot":
        snapshot.unlink()
    else:
        path = tmp_path / entry['source'] if target == "source" else snapshot
        path.write_bytes(path.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="frozen (grade|snapshot)"):
        load_signed_runs(tmp_path)
