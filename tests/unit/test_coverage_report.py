import json

from scripts.coverage_report import build


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
