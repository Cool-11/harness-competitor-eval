import json
import sys
from pathlib import Path

import pytest

from _util import REPO

sys.path.insert(0, str(REPO / "scripts"))
import cli_batch  # noqa: E402


def _write_plan(path: Path, root: Path, *, executable: str, version_command=None):
    adapter = {
        "command": [executable, "-c", "import sys; print(sys.stdin.read())"],
        "version_command": version_command or [executable, "--version"],
    }
    plan = {
        "schema_version": 1,
        "batch_id": "unit-cli-batch",
        "root": str(root),
        "defaults": {"timeout_seconds": 30},
        "adapters": {"dsh": adapter},
        "slots": [{"case": "S06", "product": "dsh", "run": "auto"}],
    }
    path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    return plan


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_batch.sbatch, "TMP_ROOT", tmp_path / "tmp")
    monkeypatch.setattr(cli_batch.sbatch, "SBATCH", tmp_path / "out")
    return tmp_path


def test_resolve_freezes_auto_run_before_prepare(sandbox):
    plan_path = sandbox / "plan.json"
    plan = _write_plan(plan_path, sandbox / "runs", executable=sys.executable)
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    assert resolved["slots"][0]["run"] == 1
    assert resolved["protocol_version"] == "hev-v3"
    assert (ledger / "resolved-plan.json").is_file()
    work = sandbox / "runs" / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    assert not work.exists()


def test_preflight_failure_does_not_prepare_or_call_model(sandbox):
    plan_path = sandbox / "plan.json"
    plan = _write_plan(plan_path, sandbox / "runs", executable="missing-dsh-test-command")
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    passed, receipt = cli_batch.preflight(resolved, ledger)
    assert passed is False
    assert receipt["products"][0]["reason"] == "executable_not_found"
    assert not (sandbox / "runs" / "S06-artifact-deep-path").exists()


def test_same_model_track_rejects_unfrozen_contract(sandbox):
    plan_path = sandbox / "plan.json"
    plan = _write_plan(plan_path, sandbox / "runs", executable=sys.executable)
    plan["comparison_track"] = "A_same_model_cli"
    plan["slots"].append({"case": "S06", "product": "codex", "run": "auto"})
    errors = cli_batch.validate_plan(plan)
    assert "A_same_model_cli 必须提供 control_contract 对象" in errors
    assert any("configuration_evidence" in error for error in errors)


def test_default_dsh_command_uses_official_headless_profile(sandbox):
    plan_path = sandbox / "plan.json"
    plan = {
        "schema_version": 1,
        "batch_id": "unit-headless-command",
        "root": str(sandbox / "runs"),
        "adapters": {"dsh": {"executable": "dsh"}},
        "slots": [{"case": "S06", "product": "dsh", "run": 1}],
    }
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    resolved, _ = cli_batch.resolve_plan(plan_path, plan)
    work = sandbox / "runs" / "S06-artifact-deep-path" / "dsh" / "run1" / "work"
    assert cli_batch._adapter_command(resolved, resolved["slots"][0], work) == [
        "dsh", "--profile", "headless"
    ]


def test_find_dsh_session_requires_new_log_with_matching_cwd(sandbox):
    root = sandbox / "dsh-sessions"
    work = sandbox / "runs" / "work"
    work.mkdir(parents=True)
    before = cli_batch._session_snapshot(root)
    session = root / "workspace" / "session-id" / "session.v4.jsonl"
    session.parent.mkdir(parents=True)
    session.write_text(
        json.dumps({"type": "session", "cwd": str(work)}) + "\n"
        + json.dumps({
            "type": "request/context",
            "data": {"model": "unit-model", "provider": "unit-provider"},
        }) + "\n"
        + json.dumps({
            "type": "request/header",
            "data": {"header": {
                "config": {
                    "model": "unit-model", "provider": "unit-provider", "reasoningEffort": "high",
                },
                "tools": [{"name": "write"}, {"name": "shell"}],
            }},
        }) + "\n"
        + json.dumps({
            "type": "permission/preset", "data": {"preset": "workspace-write"},
        }) + "\n",
        encoding="utf-8",
    )
    assert cli_batch._find_dsh_session(root, before, work) == session.resolve()
    assert cli_batch._dsh_request_context(session) == {
        "model": "unit-model",
        "provider": "unit-provider",
        "reasoning": "high",
        "sampling": "provider_default",
        "tools": ["shell", "write"],
        "permissions": "workspace-write",
        "source": str(session.resolve()),
    }


def test_codex_batch_uses_and_removes_isolated_home(sandbox):
    auth = sandbox / "auth.json"
    auth.write_text("{}", encoding="utf-8")
    plan_path = sandbox / "codex-plan.json"
    plan = {
        "schema_version": 1,
        "batch_id": "unit-codex-isolation",
        "root": str(sandbox / "runs"),
        "adapters": {
            "codex": {
                "auth_source": str(auth),
                "command": [
                    sys.executable, "-c",
                    "import os,pathlib; p=pathlib.Path(os.environ['CODEX_HOME']); print(sorted(x.name for x in p.iterdir()))",
                ],
                "version_command": [sys.executable, "--version"],
            }
        },
        "slots": [{"case": "S06", "product": "codex", "run": "auto"}],
    }
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    assert cli_batch.run_batch(resolved, ledger) == 0
    runtime = sandbox / "runs" / "S06-artifact-deep-path" / "codex" / "run1" / "runner"
    assert not (runtime / "codex-home").exists()
    assert "auth.json" in (runtime / "session.jsonl").read_text(encoding="utf-8")
    run_dir = sandbox / "out" / "S06-artifact-deep-path" / "codex" / "run1"
    doc = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert doc["execution_context"]["context_policy"] == "isolated_codex_home"
    assert doc["execution_context"]["skills_state"] == "disabled"
    assert doc["execution_context"]["memory_state"] == "disabled"


def test_missing_dsh_native_session_is_preserved_as_unverified(sandbox):
    plan_path = sandbox / "missing-session-plan.json"
    plan = {
        "schema_version": 1,
        "batch_id": "unit-dsh-missing-session",
        "root": str(sandbox / "runs"),
        "adapters": {
            "dsh": {
                "executable": sys.executable,
                "session_root": str(sandbox / "empty-dsh-sessions"),
                "version_command": [sys.executable, "--version"],
            }
        },
        "slots": [{"case": "S06", "product": "dsh", "run": "auto"}],
    }
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    assert cli_batch.run_batch(resolved, ledger) == 4
    run_dir = sandbox / "out" / "S06-artifact-deep-path" / "dsh" / "run1"
    doc = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert doc["collection_verification"]["mode"] == "unverified"
    assert Path(doc["evidence"]["session_log"]).is_file()
    result = json.loads((ledger / "batch-results.json").read_text(encoding="utf-8"))
    assert result["results"][0]["status"] == "collected_unverified"


def test_run_batch_saves_raw_session_and_collects_without_adjudicating(sandbox):
    plan_path = sandbox / "plan.json"
    plan = _write_plan(plan_path, sandbox / "runs", executable=sys.executable)
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    assert cli_batch.run_batch(resolved, ledger) == 0

    run_dir = sandbox / "out" / "S06-artifact-deep-path" / "dsh" / "run1"
    doc = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert doc["protocol_version"] == "hev-v3"
    assert doc["admission_track"] == "execution_behavior"
    assert doc["collection_verification"]["mode"] == "native_trace"
    assert doc["adjudication"]["official_eligible"] is False
    archived_session = Path(doc["evidence"]["session_log"])
    assert archived_session.is_file()
    assert run_dir in archived_session.parents

    runtime = sandbox / "runs" / "S06-artifact-deep-path" / "dsh" / "run1" / "runner"
    assert (runtime / "session.log").is_file()
    assert (runtime / "native-evidence.json").is_file()
    result = json.loads((ledger / "batch-results.json").read_text(encoding="utf-8"))
    assert result["all_collected"] is True
