"""Prospective contract for the first supported DSH intervention: tool-pwsh."""
from __future__ import annotations

import math

FIELDS = (
    "experiment_id", "model", "provider", "reasoning", "sampling", "environment_id",
    "network", "permissions", "skills", "memory", "baseline_config_id", "intervention_config_id",
    "preregistration", "invalid_rule", "stop_rule", "analysis_plan",
)


def validate_contract(contract: dict) -> list[str]:
    if not isinstance(contract, dict):
        return ["M_mechanism 必须提供 control_contract"]
    errors = []
    for key in FIELDS:
        value = contract.get(key)
        if not isinstance(value, str) or value.strip().lower() in {"", "unknown", "replace_me"}:
            errors.append(f"mechanism.{key} 未冻结")
    if contract.get("component") != "tool-pwsh":
        errors.append("M_mechanism 当前仅接入已核验的 tool-pwsh 接缝")
    if contract.get("arm") not in {"C0", "C1", "C0-restored"}:
        errors.append("mechanism.arm 必须为 C0/C1/C0-restored")
    if contract.get("skills") != "disabled" or contract.get("memory") != "disabled":
        errors.append("当前机制协议要求 Skills/Memory 均 disabled")
    if contract.get("sampling") != "provider_default":
        errors.append("当前机制协议仅支持 provider_default")
    if contract.get("primary_endpoint") != "task_success":
        errors.append("当前机制协议主要终点必须为 task_success")
    if contract.get("baseline_config_id") == contract.get("intervention_config_id"):
        errors.append("基线与干预必须使用不同配置身份")
    toolsets = []
    for key in ("baseline_tools", "intervention_tools"):
        tools = contract.get(key)
        if (not isinstance(tools, list) or not tools
                or any(not isinstance(tool, str) or not tool for tool in tools)
                or len(tools) != len(set(tools))):
            errors.append(f"mechanism.{key} 必须为不重复的非空工具名数组")
            toolsets.append(set())
        else:
            toolsets.append(set(tools))
    if toolsets[0] - toolsets[1] != {"pwsh"} or toolsets[1] - toolsets[0]:
        errors.append("P2 唯一工具差异必须为 C1 移除 pwsh，其余工具保留")
    budget = contract.get("budget", {})
    for key in ("max_runs", "timeout_seconds", "max_tokens", "max_cost"):
        value = budget.get(key) if isinstance(budget, dict) else None
        if (not isinstance(value, (int, float)) or isinstance(value, bool)
                or not math.isfinite(value) or value <= 0
                or (key != "max_cost" and type(value) is not int)):
            errors.append(f"mechanism.budget.{key} 必须为正数")
    config_hashes = contract.get("configuration_sha256", {})
    for key in ("C0", "C1"):
        digest = config_hashes.get(key) if isinstance(config_hashes, dict) else None
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            errors.append(f"mechanism.configuration_sha256.{key} 未冻结")
    return errors


def verify_observed(contract: dict, observed: dict) -> list[str]:
    errors = validate_contract(contract)
    for key in ("model", "provider", "reasoning", "sampling", "permissions"):
        if observed.get(key) != contract.get(key):
            errors.append(f"运行时 {key} 与机制合同不一致")
    expected = contract.get("intervention_tools" if contract.get("arm") == "C1" else "baseline_tools", [])
    if set(observed.get("tools", [])) != set(expected):
        errors.append("运行时工具集与机制干预臂不一致")
    if not observed.get("source"):
        errors.append("缺原生请求生效证据")
    return errors
