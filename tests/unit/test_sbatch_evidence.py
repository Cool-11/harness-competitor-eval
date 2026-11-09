"""P1：脚手架回归——prepare/collect 必须产出三件套且字段齐全。"""

import json
import shutil
import sys
from pathlib import Path

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


def test_prepare_custom_root(sandbox, capsys):
    root = sandbox / "custom-root"
    assert sbatch.prepare(
        "S06", "dsh", 1, root=root, variant="path-hint",
        product_version="9.9.9",
        model="deepseek-flash", tools="fs,pwsh", permissions="workspace-write",
        skills_state="disabled", memory_state="disabled", interface_precheck="passed",
    ) == 0
    assert "version=9.9.9" in capsys.readouterr().out
    work = root / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    assert work.is_dir()
    evidence = work.parent / "evidence"
    assert evidence.is_dir()
    for name in ("session", "export-source", "original-artifacts"):
        assert (evidence / name).is_dir()
    prep = json.loads((work.parent / "prepare.json").read_text(encoding="utf-8"))
    assert prep["run_id"].startswith("hev-")
    assert prep["schema_version"] == 3
    assert prep["protocol_version"] == "hev-v3"
    assert prep["admission_track"] == "product_result"
    assert prep["root"] == str(root)
    assert prep["evidence_dir"] == str(evidence)
    assert prep["variant"] == "path-hint"
    run_doc = json.loads((work.parent / "run.json").read_text(encoding="utf-8"))
    assert run_doc["run_id"] == prep["run_id"]
    assert run_doc["record_type"] == "product_run"
    assert run_doc["binding"]["task_revision"].startswith("sha256:")
    assert prep["evaluator_revision"] == sbatch._evaluator_revision(sbatch._resolve("S06"))
    assert run_doc["binding"]["evaluator_revision"] == prep["evaluator_revision"]
    assert run_doc["binding"]["product_revision"]
    assert run_doc["binding"]["product_config"]["version"]
    assert run_doc["execution_context"]["model"] == "deepseek-flash"
    assert run_doc["execution_context"]["tools"] == ["fs", "pwsh"]
    assert run_doc["environment"]["evidence_dir"] == str(evidence)


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
    assert manifest["run_id"].startswith("hev-")
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
    assert run_doc["run_id"] == manifest["run_id"]
    assert run_doc["adjudication"]["official_eligible"] is False
    assert run_doc["termination"]["turns"] == 3
    assert run_doc["evaluation"]["components"]["artifact"] == 1.0
    assert run_doc["evaluation"]["success"] == 1
    assert manifest["evaluator_revision"] == run_doc["binding"]["evaluator_revision"]


def test_collect_rejects_checker_changed_after_prepare(sandbox, monkeypatch):
    cases = sandbox / "cases"
    cases.mkdir()
    case = cases / "S06-artifact-deep-path"
    shutil.copytree(REPO / "tasks" / "second_tasks" / case.name, case)
    monkeypatch.setattr(sbatch, "CASES", cases)
    assert sbatch.prepare("S06", "dsh", 1) == 0
    work = sandbox / "tmp" / case.name / "dsh" / "run1" / "work"
    _install_golden(work)
    with (case / "checker.py").open("a", encoding="utf-8") as fh:
        fh.write("\n# changed after prepare\n")
    assert sbatch.collect("S06", "dsh", 1, str(work)) == 3
    assert not _out(sandbox).exists()


def test_collect_preserves_preexisting_v3_prepare_without_evaluator_revision(sandbox):
    assert sbatch.prepare("S06", "dsh", 1) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    prep_path = work.parent / "prepare.json"
    prep = json.loads(prep_path.read_text(encoding="utf-8"))
    prep.pop("evaluator_revision")
    prep_path.write_text(json.dumps(prep), encoding="utf-8")
    _install_golden(work)
    assert sbatch.collect("S06", "dsh", 1, str(work)) == 0
    manifest = json.loads((_out(sandbox) / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["evaluator_revision"] == ""


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


def test_results_row_matches_header_width(sandbox):
    """回归：collect 曾以 8 列写入 10 列表头，整行右移 → exit/时间/备注全错列。"""
    assert sbatch.prepare("S06", "dsh", 1) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    _install_golden(work)
    assert sbatch.collect("S06", "dsh", 1, str(work), variant="swap-P2") == 0

    lines = (sandbox / "out" / "results.md").read_text(encoding="utf-8").splitlines()
    cells = lambda s: [c.strip() for c in s.strip().strip("|").split("|")]
    header = next(l for l in lines if l.startswith("| 题 |"))
    row = next(l for l in lines if l.startswith("| S06-"))

    assert len(cells(row)) == len(cells(header)) == 10
    assert cells(row)[7] == "exit=0"      # exit 落在 checker exit 列
    assert "run_id=hev-" in cells(row)[-1]
    assert "variant=swap-P2" in cells(row)[-1]  # run_id 与 variant 均落在备注列


def test_prepare_refuses_to_overwrite_existing_run_slot(sandbox):
    assert sbatch.prepare("S06", "dsh", 1) == 0
    assert sbatch.prepare("S06", "dsh", 1) == 3


def test_adjudication_and_formal_report(sandbox):
    assert sbatch.prepare(
        "S06", "codex", 1,
        model="gpt-test", tools="fs", permissions="workspace-write",
        skills_state="disabled", memory_state="disabled", interface_precheck="passed",
    ) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "codex" / "run1" / "work"
    _install_golden(work)
    cwd_log = sandbox / "native-cwd.txt"
    cwd_log.write_text(str(work), encoding="utf-8")
    assert sbatch.collect("S06", "codex", 1, str(work),
                          observed_cwd=str(work), cwd_evidence=str(cwd_log),
                          evidence_mode="native_trace", session_export=str(cwd_log)) == 0
    assert sbatch.adjudicate(
        "S06", "codex", 1,
        evidence_grade="C", final_ruling="pass", rules_frozen="yes",
        task_valid="yes", evidence_valid="yes", uncontaminated="yes",
        adjudicator="tester",
    ) == 0
    run_doc = json.loads((_out(sandbox, product="codex") / "run.json").read_text(encoding="utf-8"))
    assert run_doc["adjudication"]["official_eligible"] is True

    assert sbatch.formal_report() == 0
    report = json.loads((sandbox / "out" / "formal-results.json").read_text(encoding="utf-8"))
    assert len(report["included"]) == 1
    assert report["included"][0]["run_id"] == run_doc["run_id"]


def test_codex_memory_or_skills_blocks_official_eligibility(sandbox):
    assert sbatch.prepare(
        "S06", "codex", 1,
        skills_state="enabled", memory_state="disabled",
    ) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "codex" / "run1" / "work"
    _install_golden(work)
    assert sbatch.collect("S06", "codex", 1, str(work)) == 0
    assert sbatch.adjudicate(
        "S06", "codex", 1,
        evidence_grade="C", final_ruling="pass", rules_frozen="yes",
        task_valid="yes", evidence_valid="yes", uncontaminated="yes",
        adjudicator="tester",
    ) == 0
    doc = json.loads((_out(sandbox, product="codex") / "run.json").read_text(encoding="utf-8"))
    assert doc["adjudication"]["official_eligible"] is False
    assert "Codex Skills 未证实关闭" in doc["adjudication"]["exclusion_reasons"]


def test_collect_rejects_misrouted_and_duplicate_runs_without_writing(sandbox):
    assert sbatch.prepare("S06", "dsh", 1) == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    wrong = sandbox / "other" / "work"
    shutil.copytree(work, wrong)
    shutil.copy2(work.parent / "prepare.json", wrong.parent / "prepare.json")
    shutil.copy2(work.parent / "run.json", wrong.parent / "run.json")
    out = _out(sandbox)
    assert sbatch.collect("S06", "dsh", 1, str(wrong)) == 3
    assert not out.exists()
    cwd_log = sandbox / "cwd.txt"
    cwd_log.write_text(str(wrong), encoding="utf-8")
    assert sbatch.collect("S06", "dsh", 1, str(work),
                          observed_cwd=str(wrong), cwd_evidence=str(cwd_log)) == 3
    assert not out.exists()
    _install_golden(work)
    cwd_log.write_text(str(work), encoding="utf-8")
    assert sbatch.collect("S06", "dsh", 1, str(work),
                          observed_cwd=str(work), cwd_evidence=str(cwd_log),
                          evidence_mode="native_trace", session_export=str(cwd_log)) == 0
    previous = (out / "run.json").read_bytes()
    assert sbatch.collect("S06", "dsh", 1, str(work),
                          observed_cwd=str(work), cwd_evidence=str(cwd_log)) == 3
    assert (out / "run.json").read_bytes() == previous


def test_screen_recording_can_be_admitted_with_human_ruling(sandbox):
    assert sbatch.prepare("S06", "workbuddy", 1, interface_precheck="passed") == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "workbuddy" / "run1" / "work"
    _install_golden(work)
    shot = sandbox / "start.png"
    video = sandbox / "session.mp4"
    export = sandbox / "export.png"
    for path in (shot, video, export):
        path.write_bytes(b"evidence")
    assert sbatch.collect("S06", "workbuddy", 1, str(work),
                          evidence_mode="screen_recording", preflight_shot=str(shot),
                          recording=str(video), export_evidence=str(export)) == 0
    out = _out(sandbox, product="workbuddy")
    doc = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert doc["collection_verification"]["screen_recording_scope"] == "visible_actions_only"
    assert doc["adjudication"]["official_eligible"] is False
    assert sbatch.adjudicate(
        "S06", "workbuddy", 1, evidence_grade="C", final_ruling="pass",
        rules_frozen="yes", task_valid="yes", evidence_valid="yes",
        uncontaminated="yes", adjudicator="human-reviewed-visible-evidence",
    ) == 0
    doc = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert doc["adjudication"]["official_eligible"] is True


def test_desktop_export_replaces_mandatory_recording_in_v3(sandbox):
    assert sbatch.prepare("S06", "yuanbao", 1, interface_precheck="passed") == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "yuanbao" / "run1" / "work"
    _install_golden(work)
    before = sandbox / "before.png"
    complete = sandbox / "complete.png"
    session = sandbox / "conversation.zip"
    export = sandbox / "export-source.png"
    for path in (before, complete, session, export):
        path.write_bytes(b"evidence")
    assert sbatch.collect(
        "S06", "yuanbao", 1, str(work), evidence_mode="desktop_export",
        preflight_shot=str(before), completion_shot=str(complete),
        session_export=str(session), export_evidence=str(export),
    ) == 0
    out = _out(sandbox, product="yuanbao")
    doc = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert doc["collection_verification"]["claim_scope"] == "product_result"
    assert "recording" not in doc["collection_verification"]["evidence"]
    session_record = doc["collection_verification"]["evidence"]["session_export"]
    assert Path(session_record["path"]).is_file()
    assert session_record["source_path"] == str(session.resolve())
    assert sbatch.adjudicate(
        "S06", "yuanbao", 1, evidence_grade="C", final_ruling="pass",
        rules_frozen="yes", task_valid="yes", evidence_valid="yes",
        uncontaminated="yes", adjudicator="desktop-export-reviewer",
    ) == 0
    doc = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert doc["adjudication"]["official_eligible"] is True


def test_desktop_export_rejects_missing_session_log_without_writing(sandbox):
    assert sbatch.prepare("S06", "doubao", 1, interface_precheck="passed") == 0
    work = sandbox / "tmp" / "S06-artifact-deep-path" / "doubao" / "run1" / "work"
    _install_golden(work)
    before = sandbox / "before.png"
    complete = sandbox / "complete.png"
    export = sandbox / "export-source.png"
    for path in (before, complete, export):
        path.write_bytes(b"evidence")
    assert sbatch.collect(
        "S06", "doubao", 1, str(work), evidence_mode="desktop_export",
        preflight_shot=str(before), completion_shot=str(complete),
        export_evidence=str(export),
    ) == 3
    assert not _out(sandbox, product="doubao").exists()


def test_harness_causal_pair_requires_same_frozen_contract(sandbox):
    contract = {
        "contract_id": "unit-same-model-v1",
        "only_variable": "harness",
        "model": "shared-model",
        "provider": "openai",
        "reasoning": "fixed-medium",
        "sampling": "provider_default",
        "environment_id": "unit-windows-host",
        "network": "not_used_and_trace_verified",
        "skills": "disabled",
        "memory": "disabled",
        "permissions": "workspace-write",
        "harness_components": [
            "system_prompt", "toolset", "orchestration", "context_management", "stop_policy",
        ],
    }
    for product in ("codex", "dsh"):
        context_policy = "isolated_codex_home" if product == "codex" else "headless_new_agent"
        harness_tools = "codex-shell,codex-filesystem" if product == "codex" else "dsh-pwsh,dsh-write"
        config_snapshot = sandbox / f"{product}-config-snapshot.json"
        config_snapshot.write_text(json.dumps({"product": product, "frozen": True}), encoding="utf-8")
        assert sbatch.prepare(
            "S06", product, 1, model=contract["model"], provider=contract["provider"],
            reasoning=contract["reasoning"], sampling=contract["sampling"],
            network=contract["network"], tools=harness_tools,
            permissions=contract["permissions"], skills_state="disabled",
            memory_state="disabled", interface_precheck="passed", surface="cli",
            context_policy=context_policy, admission_track="execution_behavior",
            comparison_track="A_same_model_cli", control_contract=contract,
            configuration_evidence=str(config_snapshot),
        ) == 0
        work = sandbox / "tmp" / "S06-artifact-deep-path" / product / "run1" / "work"
        _install_golden(work)
        session = sandbox / f"{product}-session.log"
        cwd_evidence = sandbox / f"{product}-cwd.json"
        session.write_text("raw session", encoding="utf-8")
        cwd_evidence.write_text(json.dumps({"cwd": str(work)}), encoding="utf-8")
        assert sbatch.collect(
            "S06", product, 1, str(work), observed_cwd=str(work),
            cwd_evidence=str(cwd_evidence), evidence_mode="native_trace",
            session_export=str(session), observed_model=contract["model"],
            observed_provider=contract["provider"],
            observed_reasoning=contract["reasoning"],
            observed_sampling=contract["sampling"],
            observed_tools=harness_tools,
            observed_permissions=contract["permissions"],
            observed_context_source=f"unit-{product}-native",
            configuration_evidence=str(config_snapshot),
        ) == 0
        assert sbatch.adjudicate(
            "S06", product, 1, evidence_grade="A", final_ruling="pass",
            rules_frozen="yes", task_valid="yes", evidence_valid="yes",
            uncontaminated="yes", adjudicator="unit-reviewer",
        ) == 0

    assert sbatch.formal_report() == 0
    report = json.loads((sandbox / "out" / "formal-results.json").read_text(encoding="utf-8"))
    assert len(report["causal_pairs"]) == 1
    paired = [row for row in report["included"] if row["causal_eligible"]]
    assert {row["product"] for row in paired} == {"codex", "dsh"}


def test_causal_readiness_rejects_runtime_model_mismatch():
    contract = {
        "contract_id": "unit-contract",
        "only_variable": "harness",
        "model": "expected-model",
        "provider": "openai",
        "reasoning": "high",
        "sampling": "provider_default",
        "environment_id": "unit-windows-host",
        "network": "not_used_and_trace_verified",
        "skills": "disabled",
        "memory": "disabled",
        "permissions": "workspace-write",
        "harness_components": sorted(sbatch.HARNESS_TREATMENT_COMPONENTS),
    }
    ready, reasons = sbatch._causal_readiness({
        "product": "dsh",
        "comparison_track": "A_same_model_cli",
        "admission_track": "execution_behavior",
        "control_contract": contract,
        "control_contract_sha256": "frozen",
        "execution_context": {
            "surface": "cli", "context_policy": "headless_new_agent",
            "network": "not_used_and_trace_verified", "skills_state": "disabled",
            "memory_state": "disabled", "permissions": "workspace-write",
            "tools": ["dsh-write"],
            "configuration_evidence_sha256": "config-hash",
        },
        "execution_context_observed": {
            "model": "different-model", "provider": "openai",
            "reasoning": "high", "sampling": "provider_default",
            "tools": ["dsh-write"], "permissions": "workspace-write",
            "source": "native-session",
        },
        "collection_verification": {
            "mode": "native_trace",
            "evidence": {"configuration_evidence": {"sha256": "config-hash"}},
        },
    })
    assert ready is False
    assert "运行时 model 与控制合同不一致" in reasons
