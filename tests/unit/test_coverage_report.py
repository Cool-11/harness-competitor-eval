import json
import datetime

from scripts.coverage_report import build, render


def test_coverage_counts_only_admitted_cells(tmp_path):
    batch = tmp_path / "S-batch"
    slot = batch / "S11-corrupt-recovery" / "dsh" / "run1"
    slot.mkdir(parents=True)
    (slot / "run.json").write_text(json.dumps({
        "schema_version": 2, "run_id": "run-1", "task": "S11-corrupt-recovery",
        "product": "dsh", "trial": 1,
        "binding": {"task_revision": "sha256:test"},
        "execution_context": {"product_version": "v1", "interface_precheck": "passed"},
        "diagnostics": {"evidence_grade": "C"},
        "adjudication": {"rules_frozen": "yes", "task_valid": "yes",
                         "evidence_valid": "yes", "uncontaminated": "yes",
                         "final_ruling": "pass"},
    }), encoding="utf-8")
    result = build(batch)
    assert result["planned_cells"] == 10
    assert result["observed_run_records"] == 1
    assert result["formal_run_records"] == 1
    assert result["formal_cells"] == 1
    assert result["ruling_counts"]["pass"] == 1
    assert "pass **1**" in render(result)


def test_coverage_keeps_invalid_pending_and_unknown_separate(tmp_path):
    batch = tmp_path / "S-batch"
    for index, ruling in enumerate(("invalid", "pending", "unknown", "fail"), 1):
        slot = batch / "S11-corrupt-recovery" / "dsh" / f"run{index}"
        slot.mkdir(parents=True)
        (slot / "run.json").write_text(json.dumps({
            "run_id": f"run-{index}", "trial": index,
            "adjudication": {"final_ruling": ruling},
        }), encoding="utf-8")
    result = build(batch)
    assert result["ruling_counts"] == {
        "pass": 0, "fail": 1, "invalid": 1, "pending": 1,
        "unknown": 1, "not_applicable": 0,
    }
    assert result["formal_run_records"] == 0


def test_cutoff_does_not_backdate_later_adjudication_or_replacement(tmp_path):
    batch = tmp_path / "S-batch"
    ids = ("invalid-1", "pass-2")
    for trial, run_id in enumerate(ids, 1):
        slot = batch / "S06-artifact-deep-path" / "codex" / f"run{trial}"
        slot.mkdir(parents=True)
        (slot / "manifest.json").write_text(json.dumps({
            "ended_at": f"2026-11-07T0{trial}:00:00+08:00",
        }), encoding="utf-8")
        (slot / "run.json").write_text(json.dumps({
            "schema_version": 2, "run_id": run_id, "trial": trial,
            "binding": {"task_revision": "sha256:test"},
            "execution_context": {"product_version": "v1", "interface_precheck": "passed"},
            "diagnostics": {"evidence_grade": "C"},
            "adjudication": {"rules_frozen": "yes", "task_valid": "yes",
                             "evidence_valid": "yes", "uncontaminated": "yes",
                             "final_ruling": "invalid" if trial == 1 else "pass",
                             "adjudicated_at": f"2026-11-0{7 if trial == 1 else 9}T03:00:00+08:00"},
        }), encoding="utf-8")
    links = tmp_path / "links.json"
    links.write_text(json.dumps([{"from_run_id": ids[0], "to_run_id": ids[1],
                                  "evidence": "review.md"}]), encoding="utf-8")
    cutoff = datetime.datetime.fromisoformat("2026-11-07T03:30:00+08:00")
    result = build(batch, cutoff, links)
    assert result["ruling_counts"]["invalid"] == 1
    assert result["ruling_counts"]["pending"] == 1
    assert result["formal_run_records"] == 0
    assert len(result["replacement_links"]) == 1
    earlier = build(batch, datetime.datetime.fromisoformat("2026-11-07T01:30:00+08:00"), links)
    assert earlier["observed_run_records"] == 1
    assert earlier["replacement_links"] == []
