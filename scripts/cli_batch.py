#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Codex / DSH CLI 的前瞻批量运行器。

只负责：计划解析、CLI 预检、逐槽 prepare、一次发射、原始日志保存和 collect。
它不会自动终裁，也不会把 CLI 进程成功退出当作任务通过。
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import dsh_export
import sbatch


SUPPORTED_PRODUCTS = {"codex", "dsh"}
PLAN_SCHEMA_VERSION = 1
CONTROL_FIELDS = {
    "contract_id", "only_variable", "model", "provider", "reasoning",
    "sampling", "environment_id", "network", "skills", "memory", "permissions",
    "harness_components",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_plan(path: Path) -> dict:
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取计划：{exc}") from exc
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise ValueError(f"只支持 schema_version={PLAN_SCHEMA_VERSION}")
    batch_id = plan.get("batch_id", "")
    if not isinstance(batch_id, str) or not batch_id.strip():
        raise ValueError("batch_id 不能为空")
    if not isinstance(plan.get("slots"), list) or not plan["slots"]:
        raise ValueError("slots 必须是非空数组")
    if not isinstance(plan.get("adapters", {}), dict):
        raise ValueError("adapters 必须是对象")
    return plan


def _case_dir(case: str) -> Path:
    cdir = sbatch._resolve(case)
    if cdir is None:
        raise ValueError(f"找不到题包：{case}")
    return cdir


def _slot_work(root: Path, case: str, product: str, run: int) -> Path:
    return root / _case_dir(case).name / product / f"run{run}" / "work"


def _slot_out(case: str, product: str, run: int) -> Path:
    return sbatch.SBATCH / _case_dir(case).name / product / f"run{run}"


def _next_run(root: Path, case: str, product: str, reserved: set[tuple[str, str, int]]) -> int:
    run = 1
    while True:
        key = (_case_dir(case).name, product, run)
        if (key not in reserved
                and not _slot_work(root, case, product, run).parent.exists()
                and not _slot_out(case, product, run).exists()):
            return run
        run += 1


def validate_plan(plan: dict) -> list[str]:
    errors = []
    comparison_track = plan.get("comparison_track", "B_native_product")
    if comparison_track not in sbatch.COMPARISON_TRACKS:
        errors.append(f"comparison_track 不受支持：{comparison_track}")
    seen = set()
    products_by_case: dict[str, set[str]] = {}
    for index, slot in enumerate(plan.get("slots", []), start=1):
        prefix = f"slots[{index - 1}]"
        if not isinstance(slot, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        case = slot.get("case", "")
        product = slot.get("product", "")
        if not isinstance(case, str) or not case:
            errors.append(f"{prefix}.case 不能为空")
        else:
            try:
                case = _case_dir(case).name
            except ValueError as exc:
                errors.append(str(exc))
        if product not in SUPPORTED_PRODUCTS:
            errors.append(f"{prefix}.product 只允许 codex/dsh")
        elif isinstance(case, str) and case:
            products_by_case.setdefault(case, set()).add(product)
        run = slot.get("run", "auto")
        if run != "auto" and (not isinstance(run, int) or isinstance(run, bool) or run < 1):
            errors.append(f"{prefix}.run 必须是正整数或 auto")
        if isinstance(run, int):
            key = (case, product, run)
            if key in seen:
                errors.append(f"重复运行槽：{key}")
            seen.add(key)
        timeout = slot.get("timeout_seconds", plan.get("defaults", {}).get("timeout_seconds", 1800))
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 1:
            errors.append(f"{prefix}.timeout_seconds 必须是正整数")
    for product in {slot.get("product") for slot in plan.get("slots", []) if isinstance(slot, dict)}:
        adapter = plan.get("adapters", {}).get(product, {})
        if not isinstance(adapter, dict):
            errors.append(f"adapters.{product} 必须是对象")
            continue
        if product == "codex":
            approval_mode = adapter.get("approval_mode", "sandbox")
            if approval_mode not in {"sandbox", "approve_for_me"}:
                errors.append("adapters.codex.approval_mode 只允许 sandbox/approve_for_me")
            if approval_mode == "approve_for_me" and "sandbox" in adapter:
                errors.append("approve_for_me 与 sandbox 互斥；请删除 adapters.codex.sandbox")
        required_env = adapter.get("required_env", [])
        if (not isinstance(required_env, list)
                or any(not isinstance(name, str) or not name.strip() for name in required_env)):
            errors.append(f"adapters.{product}.required_env 必须是字符串名数组")
        command = adapter.get("command")
        if command is not None and (
            not isinstance(command, list) or not command
            or any(not isinstance(part, str) or not part for part in command)
        ):
            errors.append(f"adapters.{product}.command 必须是非空字符串数组")
    if comparison_track == "A_same_model_cli":
        contract = plan.get("control_contract")
        if not isinstance(contract, dict):
            errors.append("A_same_model_cli 必须提供 control_contract 对象")
            contract = {}
        for key in sorted(CONTROL_FIELDS):
            value = contract.get(key)
            if value is None or value == "" or (
                isinstance(value, str) and value.strip().lower() in {"unknown", "replace_me"}
            ):
                errors.append(f"control_contract.{key} 未冻结")
        if contract.get("only_variable") != "harness":
            errors.append("control_contract.only_variable 必须是 harness")
        components = contract.get("harness_components", [])
        if not isinstance(components, list) or not sbatch.HARNESS_TREATMENT_COMPONENTS.issubset(set(components)):
            errors.append("control_contract.harness_components 未完整声明 Harness treatment")
        if contract.get("sampling") != "provider_default":
            errors.append("A_same_model_cli 当前只接受双方均不覆盖采样参数的 provider_default")
        if contract.get("network") not in {"blocked_externally", "not_used_and_trace_verified"}:
            errors.append("control_contract.network 只允许 blocked_externally/not_used_and_trace_verified")
        if contract.get("skills") != "disabled":
            errors.append("A_same_model_cli 的 Skills 必须冻结为 disabled")
        if contract.get("memory") != "disabled":
            errors.append("A_same_model_cli 的 Memory 必须冻结为 disabled")
        for case, products in products_by_case.items():
            if products != SUPPORTED_PRODUCTS:
                errors.append(f"A_same_model_cli 的 {case} 必须同时包含 codex 与 dsh")
        for product in SUPPORTED_PRODUCTS:
            adapter = plan.get("adapters", {}).get(product, {})
            if adapter.get("command") is not None:
                errors.append(f"A_same_model_cli 禁止 adapters.{product}.command 覆盖标准启动命令")
            for key in ("model", "provider", "reasoning", "sampling"):
                if adapter.get(key) != contract.get(key):
                    errors.append(f"adapters.{product}.{key} 必须与 control_contract 一致")
            adapter_permissions = adapter.get("sandbox") if product == "codex" else adapter.get("permissions")
            if adapter_permissions != contract.get("permissions"):
                errors.append(f"adapters.{product} 权限策略必须与 control_contract 一致")
            tools = adapter.get("tools")
            tools_unfrozen = (
                not tools
                or (isinstance(tools, str) and tools.strip().lower() in {"unknown", "replace_me"})
                or (isinstance(tools, list) and any(
                    not isinstance(item, str) or item.strip().lower() in {"unknown", "replace_me"}
                    for item in tools
                ))
            )
            if tools_unfrozen:
                errors.append(f"adapters.{product}.tools 必须记录该 Harness 的实际工具集")
            snapshot = adapter.get("configuration_evidence", "")
            if not snapshot or not Path(snapshot).is_file():
                errors.append(f"adapters.{product}.configuration_evidence 必须指向配置快照原件")
        if plan.get("adapters", {}).get("dsh", {}).get("profile", "headless") != "headless":
            errors.append("A_same_model_cli 的 DSH 必须使用官方 headless 一次性任务 profile")
        if plan.get("adapters", {}).get("codex", {}).get("provider") != "openai":
            errors.append("A_same_model_cli 的隔离 Codex CLI 只接受内置 openai provider")
    return errors


def _ledger_dir(plan: dict) -> Path:
    root = Path(plan.get("root") or sbatch.TMP_ROOT)
    return root / "_batch-ledger" / plan["batch_id"]


def resolve_plan(plan_path: Path, plan: dict) -> tuple[dict, Path]:
    errors = validate_plan(plan)
    if errors:
        raise ValueError("；".join(errors))
    ledger = _ledger_dir(plan)
    resolved_path = ledger / "resolved-plan.json"
    source_sha = _sha256(plan_path)
    if resolved_path.is_file():
        resolved = json.loads(resolved_path.read_text(encoding="utf-8"))
        if resolved.get("source_plan_sha256") != source_sha:
            raise ValueError("计划在 resolved-plan.json 生成后发生变化；请新建 batch_id")
        return resolved, ledger
    if ledger.exists() and any(ledger.iterdir()):
        raise ValueError(f"批次账目录非空且缺 resolved-plan.json：{ledger}")

    root = Path(plan.get("root") or sbatch.TMP_ROOT)
    reserved: set[tuple[str, str, int]] = set()
    slots = []
    for source in plan["slots"]:
        slot = dict(source)
        case_name = _case_dir(slot["case"]).name
        run = slot.get("run", "auto")
        if run == "auto":
            run = _next_run(root, case_name, slot["product"], reserved)
        key = (case_name, slot["product"], run)
        if key in reserved:
            raise ValueError(f"重复运行槽：{key}")
        reserved.add(key)
        slot["case"] = case_name
        slot["run"] = run
        slot["slot_id"] = slot.get("slot_id") or f"{case_name}__{slot['product']}__r{run}"
        slots.append(slot)

    resolved = dict(plan)
    resolved.update({
        "resolved_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_plan": str(plan_path.resolve()),
        "source_plan_sha256": source_sha,
        "protocol_version": sbatch.CURRENT_PROTOCOL,
        "root": str(root.resolve()),
        "slots": slots,
    })
    _write_json(resolved_path, resolved)
    return resolved, ledger


def _executable_path(name: str) -> str | None:
    path = Path(name)
    if path.is_file():
        return str(path.resolve())
    return shutil.which(name)


def _codex_auth_source(adapter: dict) -> Path:
    configured = adapter.get("auth_source")
    if configured:
        return Path(configured)
    codex_home = os.environ.get("CODEX_HOME")
    return (Path(codex_home) if codex_home else Path.home() / ".codex") / "auth.json"


def _adapter_command(resolved: dict, slot: dict, work: Path) -> list[str]:
    adapter = resolved.get("adapters", {}).get(slot["product"], {})
    model = slot.get("model", adapter.get("model", ""))
    custom = adapter.get("command")
    values = {"work": str(work), "model": str(model), "profile": str(adapter.get("profile", "headless"))}
    if custom:
        return [part.format(**values) for part in custom]
    if slot["product"] == "codex":
        command = [
            adapter.get("executable", "codex"), "exec", "--json", "--ephemeral",
            "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
        ]
        if adapter.get("approval_mode", "sandbox") == "approve_for_me":
            command.append("--approve-for-me")
        else:
            command.extend(["--sandbox", adapter.get("sandbox", "workspace-write")])
        command.extend(["-C", str(work)])
        if model:
            command.extend(["--model", model])
        reasoning = slot.get("reasoning", adapter.get("reasoning", ""))
        if reasoning and reasoning != "unknown":
            command.extend(["-c", f"model_reasoning_effort={json.dumps(reasoning)}"])
        command.extend(adapter.get("extra_args", []))
        command.append("-")
        return command
    command = [adapter.get("executable", "dsh"), "--profile", adapter.get("profile", "headless")]
    command.extend(adapter.get("extra_args", []))
    return command


def _dsh_session_root(adapter: dict) -> Path:
    configured = adapter.get("session_root")
    if configured:
        return Path(configured)
    dsh_home = os.environ.get("DSH_HOME")
    return Path(dsh_home) / "sessions" if dsh_home else Path.home() / ".dsh" / "sessions"


def _session_snapshot(root: Path) -> dict[str, tuple[int, int]]:
    if not root.is_dir():
        return {}
    return {
        str(path.resolve()): (path.stat().st_mtime_ns, path.stat().st_size)
        for path in root.rglob("session*.jsonl*") if path.is_file()
    }


def _find_dsh_session(root: Path, before: dict[str, tuple[int, int]], work: Path) -> Path:
    changed_parents = set()
    for path in root.rglob("session*.jsonl*") if root.is_dir() else []:
        if not path.is_file():
            continue
        current = (path.stat().st_mtime_ns, path.stat().st_size)
        if before.get(str(path.resolve())) != current:
            changed_parents.add(path.parent)
    matches = []
    for parent in changed_parents:
        try:
            log = dsh_export.resolve_log(parent)
            events = dsh_export.read_events(log)
        except Exception:  # 压缩器、半写入或格式异常均使该候选不能作为原生证据
            continue
        header = next((event for event in events if event.get("type") == "session"), {})
        cwd = header.get("cwd") or ""
        if cwd and Path(cwd).resolve() == work.resolve():
            matches.append(log.resolve())
    matches = sorted(set(matches))
    if len(matches) != 1:
        raise ValueError(f"DSH 原生会话定位结果应为 1，实际为 {len(matches)}：{matches}")
    return matches[0]


def _dsh_request_context(log: Path) -> dict:
    events = dsh_export.read_events(log)
    contexts = [event.get("data") or {} for event in events if event.get("type") == "request/context"]
    header_objects = [
        (event.get("data") or {}).get("header") or {}
        for event in events if event.get("type") == "request/header"
    ]
    headers = [header.get("config") or {} for header in header_objects]
    if not contexts or not header_objects:
        return {"model": "", "provider": "", "reasoning": "", "sampling": "",
                "tools": [], "permissions": "", "source": str(log.resolve())}
    models = {str(context.get("model") or "") for context in contexts}
    providers = {str(context.get("provider") or "") for context in contexts}
    header_models = {str(header.get("model") or "") for header in headers}
    header_providers = {str(header.get("provider") or "") for header in headers}
    reasoning = {str(header.get("reasoningEffort") or "") for header in headers}
    sampling_keys = {"temperature", "topP", "topK", "seed", "frequencyPenalty", "presencePenalty"}
    sampling_overrides = [{key: header[key] for key in sampling_keys if key in header} for header in headers]
    sampling = "provider_default" if all(not item for item in sampling_overrides) else "explicit_override"
    toolsets = {
        tuple(sorted(str(tool.get("name") or "") for tool in header.get("tools") or [] if tool.get("name")))
        for header in header_objects
    }
    permissions = {
        str((event.get("data") or {}).get("preset") or "")
        for event in events if event.get("type") == "permission/preset"
    }
    if (len(models) != 1 or len(providers) != 1 or len(reasoning) != 1
            or header_models != models or header_providers != providers
            or len(toolsets) != 1 or len(permissions) != 1):
        return {"model": "", "provider": "", "reasoning": "", "sampling": "",
                "tools": [], "permissions": "", "source": str(log.resolve())}
    return {
        "model": next(iter(models)),
        "provider": next(iter(providers)),
        "reasoning": next(iter(reasoning)),
        "sampling": sampling,
        "tools": list(next(iter(toolsets))),
        "permissions": next(iter(permissions)),
        "source": str(log.resolve()),
    }


def preflight(resolved: dict, ledger: Path) -> tuple[bool, dict]:
    rows = []
    ok = True
    checked = set()
    for slot in resolved["slots"]:
        product = slot["product"]
        if product in checked:
            continue
        checked.add(product)
        command = _adapter_command(resolved, slot, _slot_work(Path(resolved["root"]), slot["case"], product, slot["run"]))
        executable = _executable_path(command[0])
        row = {"product": product, "requested_executable": command[0], "resolved_executable": executable or ""}
        if not executable:
            row.update({"passed": False, "reason": "executable_not_found", "version": ""})
            ok = False
            rows.append(row)
            continue
        adapter = resolved.get("adapters", {}).get(product, {})
        required_env = adapter.get("required_env", [])
        missing_env = [name for name in required_env if not os.environ.get(name)]
        row["required_env"] = required_env
        row["missing_required_env"] = missing_env
        if missing_env:
            row.update({"passed": False, "reason": "required_env_missing", "version": ""})
            ok = False
            rows.append(row)
            continue
        if product == "codex":
            auth_source = _codex_auth_source(adapter)
            row["isolated_codex_home"] = True
            row["auth_source_available"] = auth_source.is_file()
            if not auth_source.is_file():
                row.update({"passed": False, "reason": "codex_auth_not_found", "version": ""})
                ok = False
                rows.append(row)
                continue
        snapshot = adapter.get("configuration_evidence", "")
        if snapshot:
            snapshot_path = Path(snapshot)
            row["configuration_evidence"] = str(snapshot_path.resolve())
            row["configuration_evidence_sha256"] = _sha256(snapshot_path)
        version_command = adapter.get("version_command", [executable, "--version"])
        try:
            proc = subprocess.run(version_command, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=20)
            version = (proc.stdout or proc.stderr or "").strip().splitlines()
            row.update({
                "passed": proc.returncode == 0,
                "reason": "" if proc.returncode == 0 else f"version_exit_{proc.returncode}",
                "version": version[0] if version else "unknown",
                "version_command": version_command,
            })
        except (OSError, subprocess.SubprocessError) as exc:
            row.update({"passed": False, "reason": type(exc).__name__, "version": ""})
        ok = ok and row["passed"]
        rows.append(row)
    receipt = {
        "batch_id": resolved["batch_id"],
        "checked_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "passed": ok,
        "products": rows,
    }
    _write_json(ledger / "preflight.json", receipt)
    return ok, receipt


def _preflight_version(receipt: dict, product: str) -> str:
    for row in receipt.get("products", []):
        if row.get("product") == product:
            return row.get("version", "unknown") or "unknown"
    return "unknown"


def _preflight_executable(receipt: dict, product: str) -> str:
    """Return the exact launcher validated by preflight.

    On Windows, ``shutil.which("dsh")`` commonly resolves to ``dsh.CMD``.
    Passing the original bare alias to ``Popen(..., shell=False)`` does not
    execute command scripts, so runtime must reuse the resolved path that was
    actually checked.
    """
    for row in receipt.get("products", []):
        if row.get("product") == product and row.get("passed"):
            executable = row.get("resolved_executable", "")
            if executable:
                return executable
    raise ValueError(f"{product} 缺少已通过预检的绝对启动器")


def _assert_unused_targets(resolved: dict) -> None:
    root = Path(resolved["root"])
    collisions = []
    for slot in resolved["slots"]:
        work_parent = _slot_work(root, slot["case"], slot["product"], slot["run"]).parent
        out = _slot_out(slot["case"], slot["product"], slot["run"])
        if work_parent.exists() or out.exists():
            collisions.append(f"{slot['slot_id']} -> {work_parent} / {out}")
    if collisions:
        raise ValueError("运行槽已存在，禁止覆盖：" + "；".join(collisions))


def run_batch(resolved: dict, ledger: Path) -> int:
    passed, receipt = preflight(resolved, ledger)
    if not passed:
        print(f"[错误] CLI 预检失败；未 prepare、未调用模型。见 {ledger / 'preflight.json'}")
        return 3
    _assert_unused_targets(resolved)

    root = Path(resolved["root"])
    defaults = resolved.get("defaults", {})
    comparison_track = resolved.get("comparison_track", "B_native_product")
    contract = resolved.get("control_contract", {}) if comparison_track == "A_same_model_cli" else {}
    results = []
    for slot in resolved["slots"]:
        cdir = _case_dir(slot["case"])
        product = slot["product"]
        run = slot["run"]
        adapter = resolved.get("adapters", {}).get(product, {})
        model = slot.get("model", adapter.get("model", "unknown")) or "unknown"
        if comparison_track == "A_same_model_cli":
            model = contract["model"]
            provider = contract["provider"]
            reasoning = contract["reasoning"]
            sampling = contract["sampling"]
            network = contract["network"]
            tools = slot.get("tools", adapter.get("tools", ""))
            if isinstance(tools, list):
                tools = ",".join(tools)
            permissions = contract["permissions"]
            skills_state = contract["skills"]
            memory_state = contract["memory"]
        else:
            provider = slot.get("provider", adapter.get("provider", "unknown"))
            reasoning = slot.get("reasoning", adapter.get("reasoning", "unknown"))
            sampling = slot.get("sampling", adapter.get("sampling", "unknown"))
            network = slot.get("network", defaults.get("network", "unknown"))
            tools = slot.get("tools", defaults.get("tools", "shell,filesystem"))
            permissions = slot.get("permissions", defaults.get("permissions", "workspace-write"))
            skills_state = "disabled" if product == "codex" else slot.get("skills_state", "unknown")
            memory_state = "disabled" if product == "codex" else slot.get("memory_state", "unknown")
        prepare_code = sbatch.prepare(
            cdir.name, product, run, root=root,
            variant=slot.get("variant", resolved.get("variant", "cli-batch-v3")),
            model=model,
            provider=provider, reasoning=reasoning, sampling=sampling,
            tools=tools, permissions=permissions, network=network,
            skills_state=skills_state, memory_state=memory_state,
            interface_precheck="passed",
            protocol_version=sbatch.CURRENT_PROTOCOL,
            admission_track="execution_behavior",
            surface="cli",
            context_policy="isolated_codex_home" if product == "codex" else "headless_new_agent",
            product_version=_preflight_version(receipt, product),
            configuration_evidence=adapter.get("configuration_evidence", ""),
            comparison_track=comparison_track,
            control_contract=contract,
        )
        if prepare_code != 0:
            results.append({"slot_id": slot["slot_id"], "status": "prepare_failed", "code": prepare_code})
            break

        work = _slot_work(root, cdir.name, product, run)
        runtime = work.parent / "runner"
        runtime.mkdir(parents=True, exist_ok=False)
        prompt = (cdir / "prompt.txt").read_text(encoding="utf-8")
        custom_command = bool(adapter.get("command"))
        input_mode = adapter.get("input_mode", "stdin" if product == "codex" or custom_command else "argv")
        if input_mode not in {"stdin", "argv"}:
            raise ValueError(f"{product} input_mode 只允许 stdin/argv")
        command = _adapter_command(resolved, slot, work)
        command[0] = _preflight_executable(receipt, product)
        if input_mode == "argv":
            command.append(prompt)
        if product == "codex":
            stdout_path = runtime / "session.jsonl"
        elif custom_command:
            stdout_path = runtime / "session.log"
        else:
            stdout_path = runtime / "final-response.txt"
        stderr_path = runtime / "stderr.log"
        dsh_session_root = _dsh_session_root(adapter)
        dsh_before = _session_snapshot(dsh_session_root) if product == "dsh" and not custom_command else {}
        process_env = os.environ.copy()
        isolated_codex_home = None
        if product == "codex":
            isolated_codex_home = runtime / "codex-home"
            isolated_codex_home.mkdir()
            shutil.copy2(_codex_auth_source(adapter), isolated_codex_home / "auth.json")
            process_env["CODEX_HOME"] = str(isolated_codex_home)
        started = datetime.datetime.now().astimezone()
        timed_out = False
        returncode = None
        timeout_seconds = slot.get("timeout_seconds", defaults.get("timeout_seconds", 1800))
        _write_json(runtime / "invocation.json", {
            "slot_id": slot["slot_id"], "command": command, "cwd": str(work),
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "started_at": started.isoformat(timespec="seconds"),
            "timeout_seconds": timeout_seconds,
            "codex_home_isolated": product == "codex",
        })
        try:
            with stdout_path.open("w", encoding="utf-8", newline="") as stdout_file, \
                    stderr_path.open("w", encoding="utf-8", newline="") as stderr_file:
                process = subprocess.Popen(
                    command, cwd=work, stdin=subprocess.PIPE, stdout=stdout_file, stderr=stderr_file,
                    text=True, encoding="utf-8", errors="replace", env=process_env, shell=False,
                )
                try:
                    process.communicate(prompt if input_mode == "stdin" else None, timeout=timeout_seconds)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    process.kill()
                    process.communicate()
                returncode = process.returncode
        finally:
            if isolated_codex_home is not None:
                if runtime.resolve() not in isolated_codex_home.resolve().parents:
                    raise RuntimeError("拒绝清理不在 runner 目录内的 CODEX_HOME")
                shutil.rmtree(isolated_codex_home)
        ended = datetime.datetime.now().astimezone()
        elapsed = (ended - started).total_seconds()
        termination = "timeout" if timed_out else ("product_declared_done" if returncode == 0 else "error")
        session_export = stdout_path
        observed_context = {
            "model": model if product == "codex" else "",
            "provider": provider if product == "codex" else "",
            "reasoning": reasoning if product == "codex" else "",
            "sampling": "provider_default" if product == "codex" else "",
            "tools": sbatch._csv_values(tools) if product == "codex" else [],
            "permissions": permissions if product == "codex" else "",
            "source": "codex --model + isolated CODEX_HOME" if product == "codex" else "",
        }
        if product == "dsh" and not custom_command:
            try:
                session_export = _find_dsh_session(dsh_session_root, dsh_before, work)
                observed_context = _dsh_request_context(session_export)
            except ValueError as exc:
                _write_json(runtime / "evidence-error.json", {
                    "slot_id": slot["slot_id"], "error": str(exc),
                    "session_root": str(dsh_session_root.resolve()),
                    "stdout": str(stdout_path), "stderr": str(stderr_path),
                })
                collect_code = sbatch.collect(
                    cdir.name, product, run, str(work), turns=1, elapsed=elapsed,
                    timed_out=timed_out, termination=termination,
                    observed_cwd=str(work), cwd_evidence=str(runtime / "evidence-error.json"),
                    evidence_mode="unverified", session_export=str(stdout_path),
                    configuration_evidence=adapter.get("configuration_evidence", ""),
                )
                results.append({
                    "slot_id": slot["slot_id"],
                    "status": "collected_unverified" if collect_code == 0 else "collect_failed",
                    "process_returncode": returncode, "timed_out": timed_out,
                    "runtime_dir": str(runtime), "collect_code": collect_code,
                    "error": str(exc),
                })
                break
        native_evidence = runtime / "native-evidence.json"
        _write_json(native_evidence, {
            "slot_id": slot["slot_id"], "command": command, "cwd": str(work),
            "started_at": started.isoformat(timespec="seconds"),
            "ended_at": ended.isoformat(timespec="seconds"),
            "returncode": returncode, "timed_out": timed_out,
            "session_export": str(session_export), "session_sha256": _sha256(session_export),
            "observed_context": observed_context,
            "final_stdout": str(stdout_path), "final_stdout_sha256": _sha256(stdout_path),
            "stderr": str(stderr_path), "stderr_sha256": _sha256(stderr_path),
        })
        collect_code = sbatch.collect(
            cdir.name, product, run, str(work), turns=1, elapsed=elapsed,
            timed_out=timed_out, termination=termination,
            observed_cwd=str(work), cwd_evidence=str(native_evidence),
            observed_model=observed_context["model"],
            observed_provider=observed_context["provider"],
            observed_reasoning=observed_context["reasoning"],
            observed_sampling=observed_context["sampling"],
            observed_tools=observed_context["tools"],
            observed_permissions=observed_context["permissions"],
            observed_context_source=observed_context["source"],
            evidence_mode="native_trace", session_export=str(session_export),
            configuration_evidence=adapter.get("configuration_evidence", ""),
        )
        results.append({
            "slot_id": slot["slot_id"], "status": "collected" if collect_code == 0 else "collect_failed",
            "process_returncode": returncode, "timed_out": timed_out,
            "collect_code": collect_code, "runtime_dir": str(runtime),
        })
        _write_json(ledger / "batch-results.json", {"batch_id": resolved["batch_id"], "results": results})
        if collect_code != 0:
            break

    success = len(results) == len(resolved["slots"]) and all(r["status"] == "collected" for r in results)
    _write_json(ledger / "batch-results.json", {
        "batch_id": resolved["batch_id"],
        "completed_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "all_collected": success,
        "results": results,
    })
    print(f"批次完成：all_collected={success}；终裁仍需人工执行。")
    return 0 if success else 4


def main() -> None:
    parser = argparse.ArgumentParser(description="Codex / DSH CLI 前瞻批量运行器")
    parser.add_argument("command", choices=["validate", "resolve", "preflight", "run"])
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        plan = _load_plan(args.plan)
        errors = validate_plan(plan)
        if errors:
            for error in errors:
                print(f"[错误] {error}")
            raise SystemExit(2)
        if args.command == "validate":
            print(f"计划有效：{plan['batch_id']}，{len(plan['slots'])} 个槽")
            return
        resolved, ledger = resolve_plan(args.plan, plan)
        if args.command == "resolve":
            print(f"已冻结解析计划：{ledger / 'resolved-plan.json'}")
            return
        if args.command == "preflight":
            passed, _ = preflight(resolved, ledger)
            print(f"CLI 预检：passed={passed}；{ledger / 'preflight.json'}")
            raise SystemExit(0 if passed else 3)
        raise SystemExit(run_batch(resolved, ledger))
    except ValueError as exc:
        print(f"[错误] {exc}")
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
