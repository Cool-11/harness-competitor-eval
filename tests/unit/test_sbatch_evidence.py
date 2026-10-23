"""P1：脚手架回归——prepare/collect 必须产出三件套且字段齐全。"""

import json
import shutil
import sys

import pytest

from _util import REPO

sys.path.insert(0, str(REPO / "scripts"))
import sbatch  # noqa: E402


def _install_golden(work):
    shutil.copytree(REPO / "tests" / "fixtures" / "golden" / "S06-artifact-deep-path",
                    work, dirs_exist_ok=True)


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(sbatch, "TMP_ROOT", tmp_path / "tmp")
    monkeypatch.setattr(sbatch, "SBATCH", tmp_path / "out")
    return tmp_path


def _out(tmp_path, case="S06-artifact-deep-path", product="dsh", run=1):
    return tmp_path / "out" / case / product / f"run{run}"


def test_prepare_custom_root(sandbox):
    root = sandbox / "custom-root"
    assert sbatch.prepare("S06", "dsh", 1, root=root, variant="path-hint") == 0
    work = root / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    assert work.is_dir()
    prep = json.loads((work.parent / "prepare.json").read_text(encoding="utf-8"))
    assert prep["root"] == str(root)
    assert prep["variant"] == "path-hint"
    run_doc = json.loads((work.parent / "run.json").read_text(encoding="utf-8"))
    assert run_doc["binding"]["product_revision"]
    assert run_doc["binding"]["product_config"]["version"]


def test_collect_writes_evidence(sandbox):
    assert sbatch.prepare("S06", "dsh", 1) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    assert (work.parent / "prepare.json").is_file()
    _install_golden(work)

    assert sbatch.collect("S06", "dsh", 1, str(work), interventions=2, turns=3) == 0

    out = _out(sandbox)
    for name in ("prepare.json", "manifest.json", "usage.json", "score.json",
                 "run.json", "checker_output.txt"):
        assert (out / name).is_file(), f"缺 {name}"

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    usage = json.loads((out / "usage.json").read_text(encoding="utf-8"))
    score = json.loads((out / "score.json").read_text(encoding="utf-8"))

    assert manifest["case"] == "S06-artifact-deep-path"
    assert manifest["interventions"] == 2
    assert manifest["artifacts_count"] >= 1
    assert manifest["variant"] == "default"
    assert manifest["work_dir"].endswith("work")
    assert usage["turns"] == 3
    assert usage["manual_interventions"] == 2
    assert usage["elapsed_seconds"] is not None
    assert score["raw_full"] == 7.0
    assert score["status"] == "graded"
    run_doc = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert run_doc["status"] == "scored"
    assert run_doc["termination"]["turns"] == 3
    assert run_doc["evaluation"]["components"]["artifact"] == 1.0
    assert run_doc["evaluation"]["success"] == 1


def test_summary_writes_pilot_results(sandbox):
    assert sbatch.prepare("S06", "dsh", 1) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    _install_golden(work)
    assert sbatch.collect("S06", "dsh", 1, str(work)) == 0
    assert sbatch.summary("S06", 1) == 0

    root = sandbox / "out" / "S06-artifact-deep-path"
    result = json.loads((root / "pilot-results.json").read_text(encoding="utf-8"))
    assert result["coverage"] == {"expected": 5, "found": 1, "missing": 4}
    assert result["by_product"]["dsh"]["success"] == 1
    assert (root / "pilot-summary.md").is_file()


def test_timeout_recorded(sandbox):
    assert sbatch.prepare("S06", "dsh", 2) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "dsh" / "run2" / "work"
    assert sbatch.collect("S06", "dsh", 2, str(work), timed_out=True) == 0
    usage = json.loads((_out(sandbox, run=2) / "usage.json").read_text(encoding="utf-8"))
    score = json.loads((_out(sandbox, run=2) / "score.json").read_text(encoding="utf-8"))
    assert usage["timed_out"] is True
    assert score["status"] == "timeout"
