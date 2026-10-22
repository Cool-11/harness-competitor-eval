"""P1：脚手架回归——prepare/collect 必须产出三件套且字段齐全。"""

import json
import sys

import pytest

from _util import REPO

sys.path.insert(0, str(REPO / "scripts"))
import sbatch  # noqa: E402


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(sbatch, "TMP_ROOT", tmp_path / "tmp")
    monkeypatch.setattr(sbatch, "SBATCH", tmp_path / "out")
    return tmp_path


def _out(tmp_path, case="S06-artifact-deep-path", product="dsh", run=1):
    return tmp_path / "out" / case / product / f"run{run}"


def test_collect_writes_evidence(sandbox):
    assert sbatch.prepare("S06", "dsh", 1) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    assert (work.parent / "prepare.json").is_file()

    assert sbatch.collect("S06", "dsh", 1, str(work), interventions=2, turns=3) == 0

    out = _out(sandbox)
    for name in ("manifest.json", "usage.json", "score.json", "checker_output.txt"):
        assert (out / name).is_file(), f"缺 {name}"

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    usage = json.loads((out / "usage.json").read_text(encoding="utf-8"))
    score = json.loads((out / "score.json").read_text(encoding="utf-8"))

    assert manifest["case"] == "S06-artifact-deep-path"
    assert manifest["interventions"] == 2
    assert manifest["artifacts_count"] >= 1
    assert usage["turns"] == 3
    assert usage["manual_interventions"] == 2
    assert usage["elapsed_seconds"] is not None
    assert score["raw_full"] == 7.0
    assert score["status"] == "graded"


def test_timeout_recorded(sandbox):
    assert sbatch.prepare("S06", "dsh", 2) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "dsh" / "run2" / "work"
    assert sbatch.collect("S06", "dsh", 2, str(work), timed_out=True) == 0
    usage = json.loads((_out(sandbox, run=2) / "usage.json").read_text(encoding="utf-8"))
    score = json.loads((_out(sandbox, run=2) / "score.json").read_text(encoding="utf-8"))
    assert usage["timed_out"] is True
    assert score["status"] == "timeout"
