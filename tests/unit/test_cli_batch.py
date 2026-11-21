import json
import sys
from pathlib import Path

import pytest

from _util import REPO

sys.path.insert(0, str(REPO / "scripts"))
import cli_batch  # noqa: E402

REAL_READ_PROBE = cli_batch._dsh_read_probe


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
    # These tests use fake product processes. Real read isolation is tested below.
    monkeypatch.setattr(cli_batch, "_dsh_read_probe", lambda targets: {"passed": True, "scope": "unit_mock"})
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


def test_auto_run_advances_past_archived_runs_with_new_root(sandbox):
    archive = sandbox / "out" / "S06-artifact-deep-path" / "dsh" / "run8"
    archive.mkdir(parents=True)
    plan_path = sandbox / "plan.json"
    plan = _write_plan(plan_path, sandbox / "fresh-root", executable=sys.executable)
    resolved, _ = cli_batch.resolve_plan(plan_path, plan)
    assert resolved["slots"][0]["run"] == 9


def test_preflight_failure_does_not_prepare_or_call_model(sandbox):
    plan_path = sandbox / "plan.json"
    plan = _write_plan(plan_path, sandbox / "runs", executable="missing-dsh-test-command")
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    passed, receipt = cli_batch.preflight(resolved, ledger)
    assert passed is False
    assert receipt["products"][0]["reason"] == "executable_not_found"
    assert not (sandbox / "runs" / "S06-artifact-deep-path").exists()


def test_preflight_rejects_missing_required_environment(sandbox, monkeypatch):
    plan_path = sandbox / "required-env-plan.json"
    plan = _write_plan(plan_path, sandbox / "runs", executable=sys.executable)
    plan["adapters"]["dsh"]["required_env"] = ["HEV_UNIT_MISSING_KEY"]
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    monkeypatch.delenv("HEV_UNIT_MISSING_KEY", raising=False)
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    passed, receipt = cli_batch.preflight(resolved, ledger)
    assert passed is False
    assert receipt["products"][0]["reason"] == "required_env_missing"
    assert receipt["products"][0]["missing_required_env"] == ["HEV_UNIT_MISSING_KEY"]
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


def test_runtime_reuses_absolute_launcher_validated_by_preflight():
    receipt = {
        "products": [{
            "product": "dsh",
            "passed": True,
            "resolved_executable": r"C:\Users\tester\AppData\Roaming\npm\dsh.CMD",
        }]
    }
    assert cli_batch._preflight_executable(receipt, "dsh") == (
        r"C:\Users\tester\AppData\Roaming\npm\dsh.CMD"
    )


def test_codex_approve_for_me_is_explicit_and_excludes_sandbox(sandbox):
    plan_path = sandbox / "approve-plan.json"
    plan = {
        "schema_version": 1,
        "batch_id": "unit-codex-approve",
        "root": str(sandbox / "runs"),
        "adapters": {"codex": {"executable": "codex", "approval_mode": "approve_for_me"}},
        "slots": [{"case": "S06", "product": "codex", "run": 1}],
    }
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    resolved, _ = cli_batch.resolve_plan(plan_path, plan)
    work = sandbox / "runs" / "S06-artifact-deep-path" / "codex" / "run1" / "work"
    command = cli_batch._adapter_command(resolved, resolved["slots"][0], work)
    assert "--approve-for-me" in command
    assert "--sandbox" not in command


def test_codex_approve_for_me_rejects_conflicting_sandbox(sandbox):
    plan = {
        "schema_version": 1,
        "batch_id": "unit-codex-approval-conflict",
        "root": str(sandbox / "runs"),
        "adapters": {"codex": {
            "executable": "codex", "approval_mode": "approve_for_me", "sandbox": "workspace-write",
        }},
        "slots": [{"case": "S06", "product": "codex", "run": 1}],
    }
    assert "approve_for_me 与 sandbox 互斥；请删除 adapters.codex.sandbox" in cli_batch.validate_plan(plan)


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


def test_delivery_gate_only_checks_nonempty_files_inside_work_root(sandbox):
    work = sandbox / "work"
    work.mkdir()
    (work / "result.md").write_text("A1\n", encoding="utf-8")
    (work / "error_report.md").write_text("", encoding="utf-8")
    assert cli_batch._missing_delivery_files(work, ["result.md", "error_report.md"]) == ["error_report.md"]
    (work / "error_report.md").write_text("未发现损坏\n", encoding="utf-8")
    assert cli_batch._missing_delivery_files(work, ["result.md", "error_report.md"]) == []
    (work / "result.md").unlink()
    (work / "result.md").symlink_to(sandbox / "outside.md")
    (sandbox / "outside.md").write_text("A1\n", encoding="utf-8")
    assert cli_batch._missing_delivery_files(work, ["result.md", "error_report.md"]) == ["result.md"]


def test_delivery_gate_rejects_path_escape_and_non_dsh(sandbox):
    plan = _write_plan(sandbox / "plan.json", sandbox / "runs", executable=sys.executable)
    plan["slots"][0]["delivery_gate"] = {"required_files": ["../truth.json"]}
    assert any("delivery_gate" in item for item in cli_batch.validate_plan(plan))
    plan["slots"][0]["delivery_gate"] = {"required_files": ["result.md", "error_report.md"]}
    assert cli_batch.validate_plan(plan) == []
    plan["slots"][0]["product"] = "codex"
    assert any("delivery_gate" in item for item in cli_batch.validate_plan(plan))


def test_delivery_gate_resumes_same_dsh_session_once_when_files_missing(sandbox, monkeypatch):
    plan_path = sandbox / "gate-plan.json"
    plan = {
        "schema_version": 1, "batch_id": "unit-delivery-gate", "root": str(sandbox / "runs"),
        "adapters": {"dsh": {"executable": sys.executable}},
        "slots": [{"case": "S11", "product": "dsh", "run": 1,
                   "delivery_gate": {"required_files": ["result.md", "error_report.md"]}}],
    }
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    receipt = {"products": [{"product": "dsh", "passed": True,
                             "resolved_executable": sys.executable, "version": "test"}]}
    monkeypatch.setattr(cli_batch, "preflight", lambda *_: (True, receipt))
    session = sandbox / "session.v4.jsonl"
    session.write_text("session fixture\n", encoding="utf-8")
    monkeypatch.setattr(cli_batch, "_find_dsh_session", lambda *_: session)
    monkeypatch.setattr(cli_batch.dsh_export, "read_events", lambda *_: [
        {"type": "session", "id": "session-fixture", "cwd": "fixture"}
    ])
    monkeypatch.setattr(cli_batch, "_dsh_request_context", lambda *_: {
        "model": "deepseek-flash", "provider": "deepseek-official", "reasoning": "high",
        "sampling": "provider_default", "tools": ["read", "write"],
        "permissions": "workspace-write", "source": str(session),
    })
    calls = []
    class FakeProcess:
        returncode = 0
        def __init__(self, command, *, cwd, stdout, **_):
            calls.append(command)
            self.cwd, self.stdout = Path(cwd), stdout
        def communicate(self, *_args, **_kwargs):
            if len(calls) == 2:
                (self.cwd / "result.md").write_text("A1\n", encoding="utf-8")
                (self.cwd / "error_report.md").write_text("第 3 行缺逗号\n", encoding="utf-8")
            self.stdout.write("completed\n")
    monkeypatch.setattr(cli_batch.subprocess, "Popen", FakeProcess)
    collected = []
    monkeypatch.setattr(cli_batch.sbatch, "collect", lambda *a, **kw: collected.append(kw) or 0)

    assert cli_batch.run_batch(resolved, ledger) == 0
    assert len(calls) == 2
    assert calls[1][-3:-1] == ["--session-id", "session-fixture"]
    assert "result.md" in calls[1][-1] and "error_report.md" in calls[1][-1]
    assert "checker" not in calls[1][-1] and "truth" not in calls[1][-1]
    assert collected[0]["turns"] == 2
    native = sandbox / "runs" / "S11-corrupt-recovery" / "dsh" / "run1" / "runner" / "native-evidence.json"
    assert json.loads(native.read_text(encoding="utf-8"))["delivery_gate"]["missing_after"] == []


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


def test_readable_judge_blocks_launch_before_prepare(sandbox, monkeypatch):
    monkeypatch.setattr(cli_batch, '_dsh_read_probe', REAL_READ_PROBE)
    plan_path = sandbox / 'read-isolation.json'
    plan = _write_plan(plan_path, sandbox / 'runs', executable=sys.executable)
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    assert cli_batch.run_batch(resolved, ledger) == 3
    receipt = json.loads((ledger / 'preflight.json').read_text(encoding='utf-8'))
    assert receipt['products'][0]['reason'] == 'judge_read_isolation_failed'
    assert any(row['status'] == 'readable' for row in receipt['products'][0]['read_isolation']['paths'])
    assert not (sandbox / 'out').exists()
    assert not (sandbox / 'runs' / 'S06-artifact-deep-path').exists()


@pytest.mark.parametrize('change', ['config', 'patch', 'new_input', 'plan'])
def test_dependency_drift_blocks_model_without_rewriting_frozen_plan(sandbox, monkeypatch, change):
    import shutil
    case = sandbox / 'case'
    shutil.copytree(cli_batch._case_dir('S06'), case)
    monkeypatch.setattr(cli_batch, '_case_dir', lambda _: case)
    plan_path = sandbox / 'frozen.json'
    plan = _write_plan(plan_path, sandbox / 'runs', executable=sys.executable)
    config, patch = sandbox / 'config.yml', sandbox / 'patch.yml'
    config.write_text('baseline')
    patch.write_text('patch')
    plan['adapters']['dsh'].update(configuration_evidence=str(config), extra_args=['--patch', str(patch)])
    plan_path.write_text(json.dumps(plan))
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    before = (ledger / 'resolved-plan.json').read_bytes()
    target = {'config': config, 'patch': patch, 'new_input': case / 'inputs/new.txt', 'plan': plan_path}[change]
    target.write_text('changed')
    with pytest.raises(ValueError, match='变化'):
        cli_batch.run_batch(resolved, ledger)
    assert (ledger / 'resolved-plan.json').read_bytes() == before
    assert not (sandbox / 'out').exists()


def test_mechanism_track_cannot_use_an_empty_contract(sandbox):
    plan = _write_plan(sandbox / 'plan.json', sandbox / 'runs', executable=sys.executable)
    plan['comparison_track'] = 'M_mechanism'
    errors = cli_batch.validate_plan(plan)
    assert any('control_contract' in error for error in errors)
    assert any('标准 DSH' in error for error in errors)


@pytest.mark.parametrize('failure', ['inactive', 'source_drift'])
def test_mechanism_run_preserves_evidence_and_stops_on_ineffective_or_changed_config(sandbox, monkeypatch, failure):
    import mechanism_contract
    config = sandbox / 'merged.yml'
    config.write_text('frozen config')
    prereg = sandbox / 'prereg.md'
    prereg.write_text('unit protocol; no real product runs')
    contract = {key: 'unit-frozen' for key in mechanism_contract.FIELDS}
    contract.update(component='tool-pwsh', arm='C1', skills='disabled', memory='disabled',
                    sampling='provider_default', primary_endpoint='task_success',
                    baseline_config_id='baseline', intervention_config_id='intervention',
                    baseline_tools=['pwsh', 'read', 'write'], intervention_tools=['read', 'write'],
                    preregistration=str(prereg), configuration_sha256={'C0': 'a' * 64, 'C1': cli_batch._sha256(config)},
                    budget={'max_runs': 1, 'timeout_seconds': 30, 'max_tokens': 1000, 'max_cost': 1})
    plan = {'schema_version': 1, 'batch_id': 'unit-mechanism', 'root': str(sandbox / 'runs'),
            'comparison_track': 'M_mechanism', 'control_contract': contract,
            'adapters': {'dsh': {'executable': sys.executable, 'configuration_evidence': str(config),
                                **{key: contract[key] for key in ('model', 'provider', 'reasoning', 'sampling')}}},
            'slots': [{'case': 'S11', 'product': 'dsh', 'run': 1}]}
    plan_path = sandbox / 'mechanism.json'
    plan_path.write_text(json.dumps(plan))
    assert cli_batch.validate_plan(plan) == []
    resolved, ledger = cli_batch.resolve_plan(plan_path, plan)
    receipt = {'products': [{'product': 'dsh', 'passed': True, 'resolved_executable': sys.executable, 'version': 'unit-version'}]}
    monkeypatch.setattr(cli_batch, 'preflight', lambda *_: (True, receipt))
    session = sandbox / 'session.jsonl'
    session.write_text('raw unit session')
    monkeypatch.setattr(cli_batch, '_find_dsh_session', lambda *_: session)
    observed = {key: contract[key] for key in ('model', 'provider', 'reasoning', 'sampling', 'permissions')}
    # The intervention declaration alone cannot remove pwsh from the actual request.
    observed.update(tools=contract['baseline_tools'], source=str(session))
    monkeypatch.setattr(cli_batch, '_dsh_request_context', lambda *_: observed)
    class FakeProcess:
        returncode = 0
        def __init__(self, *args, stdout, **kwargs):
            stdout.write('raw response')
        def communicate(self, *args, **kwargs):
            if failure == 'source_drift':
                config.write_text('changed while running')
    real_popen = cli_batch.subprocess.Popen
    monkeypatch.setattr(cli_batch.subprocess, 'Popen',
                        lambda *args, **kwargs: (real_popen(*args, **kwargs)
                                                if isinstance(kwargs.get('stdout'), int)
                                                else FakeProcess(*args, **kwargs)))
    assert cli_batch.run_batch(resolved, ledger) == 4
    runtime = sandbox / 'runs/S11-corrupt-recovery/dsh/run1/runner'
    assert (runtime / 'final-response.txt').read_text(encoding='utf-8') == 'raw response'
    result = json.loads((ledger / 'batch-results.json').read_text(encoding='utf-8'))
    assert result['all_collected'] is False
    if failure == 'source_drift':
        assert result['results'][0]['status'] == 'source_drift'
        assert (runtime / 'freeze-error.json').is_file()
        assert not (sandbox / 'out').exists()
    else:
        assert result['results'][0]['status'] == 'mechanism_unverified'
        run = json.loads((sandbox / 'out/S11-corrupt-recovery/dsh/run1/run.json').read_text(encoding='utf-8'))
        assert run['comparison_track'] == 'M_mechanism'
        assert run['control_contract']['experiment_id'] == contract['experiment_id']
        assert run['collection_verification']['mode'] == 'unverified'
        assert not run['adjudication']['official_eligible']
