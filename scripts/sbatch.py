#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sbatch.py — S 批（压力层）跑测脚手架

职责：把"准备一次运行 → 跑完归档 → 自动判分 → 记入结果大表"标准化，减少人为漂移。
真值/checker/prompt 的纪律见 docs/03-打分细则-v1.md（已冻结）与 docs/10。

用法：
  # 1) 准备：建工作目录、放入该题 inputs、打印投喂指令位置与哈希
  python scripts/sbatch.py prepare S06 dsh --run 1

  # 2) 跑：按 docs/05 手册，把 prompt.txt 全文粘贴给产品（新开会话），录屏/日志留痕

  # 3) 归档+判分：快照工作目录 → 跑 checker → 写结果行 + 三件套证据包
  python scripts/sbatch.py collect S06 dsh --run 1 --work "C:\\tmp_run\\S06-artifact-deep-path\\dsh\\run1\\work" --interventions 0 --turns 6
"""

import argparse
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CASES = REPO / "tasks" / "second_tasks"
SBATCH = REPO / "Log-analyse" / "S-batch"
TMP_ROOT = Path(r"C:\tmp_run")
PRODUCTS = ["codex", "dsh", "workbuddy", "yuanbao", "doubao"]
SUITE = "harness-v1"
RUN_SCHEMA_VERSION = 3
CURRENT_PROTOCOL = "hev-v3"
ADMISSION_TRACKS = {"product_result", "execution_behavior"}
COMPARISON_TRACKS = {"A_same_model_cli", "B_native_product", "M_mechanism"}
HARNESS_TREATMENT_COMPONENTS = {
    "system_prompt", "toolset", "orchestration", "context_management", "stop_policy",
}
PINS = REPO / "benchmarks" / "pins.json"
PRODUCTS_REGISTRY = REPO / "products" / "products.json"
TASK_REVISION_FILES = {"task.md", "prompt.txt", "checker.py", "spec.md", "truth.json"}


def _sha8(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:8]


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _task_revision(cdir: Path) -> str:
    """题包内容指纹；不再用只覆盖 S06 的 suite pin 代替单题版本。"""
    entries = []
    for p in sorted(f for f in cdir.rglob("*") if f.is_file()):
        rel = p.relative_to(cdir)
        if p.name not in TASK_REVISION_FILES and rel.parts[0] != "inputs":
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        entries.append(f"{rel.as_posix()}:{digest}")
    raw = "\n".join(entries).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _new_run_id(cdir: Path, product: str, run: int) -> str:
    """生成不可复用的运行身份；语义槽位另存 run_key。"""
    stamp = datetime.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    short = cdir.name.split("-")[0]
    return f"hev-{stamp}-{short}-{product}-r{run}-{uuid.uuid4().hex[:8]}"


def _csv_values(raw) -> list[str]:
    if isinstance(raw, list):
        return [str(v).strip() for v in raw if str(v).strip()]
    if not raw or str(raw).strip().lower() == "unknown":
        return []
    return [v.strip() for v in str(raw).split(",") if v.strip()]


def _suite_revision() -> str:
    try:
        return json.loads(PINS.read_text(encoding="utf-8")).get("revision", "")
    except (OSError, json.JSONDecodeError):
        return ""


def _product_config(product: str) -> dict:
    try:
        data = json.loads(PRODUCTS_REGISTRY.read_text(encoding="utf-8"))
        return data.get("products", {}).get(product, {})
    except (OSError, json.JSONDecodeError):
        return {}


def _product_revision(product: str) -> str:
    cfg = _product_config(product)
    if not cfg:
        return ""
    raw = json.dumps(cfg, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:8]


def _run_skeleton(cdir: Path, product: str, run: int, variant: str,
                  root: Path, work: Path, prep: dict) -> dict:
    run_id = prep.get("run_id") or _new_run_id(cdir, product, run)
    return {
        "schema_version": prep.get("schema_version", RUN_SCHEMA_VERSION),
        "protocol_version": prep.get("protocol_version", CURRENT_PROTOCOL),
        "admission_track": prep.get("admission_track", "product_result"),
        "comparison_track": prep.get("comparison_track", "B_native_product"),
        "control_contract": prep.get("control_contract", {}),
        "control_contract_sha256": prep.get("control_contract_sha256", ""),
        "record_type": "product_run",
        "run_id": run_id,
        "run_key": f"{cdir.name}__{product}__r{run}",
        "suite": SUITE,
        "task": cdir.name,
        "product": product,
        "trial": run,
        "variant": variant,
        "status": "prepared",
        "environment": {
            "root": str(root),
            "work_dir": str(work),
            "evidence_dir": prep.get("evidence_dir", ""),
        },
        "execution_context": prep.get("execution_context", {}),
        "binding": {
            "prompt_sha8": prep.get("prompt_sha8", ""),
            "inputs_sha8": prep.get("inputs_sha8", {}),
            "task_revision": _task_revision(cdir),
            "suite_revision": _suite_revision(),
            "product_revision": _product_revision(product),
            "product_config": _product_config(product),
            "evaluator_revision": "docs/14-v0.1",
        },
        "termination": {
            "reason": "",
            "timed_out": False,
            "turns": None,
            "manual_interventions": 0,
        },
        "evaluation": {
            "reward_basis": [],
            "components": {},
            "success": None,
            "v1": None,
        },
        "diagnostics": {
            "failure_code": "",
            "first_error": None,
            "evidence_grade": "",
        },
        "adjudication": {
            "rules_frozen": "unknown",
            "task_valid": "unknown",
            "evidence_valid": "unknown",
            "uncontaminated": "unknown",
            "final_ruling": "pending",
            "official_eligible": False,
            "exclusion_reasons": ["尚未完成人工终裁"],
            "adjudicator": "",
            "adjudicated_at": "",
            "notes": "",
        },
        "evidence": {},
    }


def _write_json(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _num(v: str):
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


def _resolve(name: str):
    """把短 id（如 S06）解析到真实用例目录（如 S06-artifact-deep-path）。"""
    d = CASES / name
    if d.is_dir():
        return d
    cands = sorted(p for p in CASES.iterdir()
                   if p.is_dir() and p.name.startswith(name + "-"))
    return cands[0] if cands else None


def prepare(case: str, product: str, run: int,
            root=None, variant: str = "default", model: str = "unknown",
            tools="", permissions: str = "unknown",
            skills_state: str = "unknown", memory_state: str = "unknown",
            interface_precheck: str = "not_run",
            protocol_version: str = CURRENT_PROTOCOL,
            admission_track: str = "product_result",
            surface: str = "desktop", context_policy: str = "default",
            product_version: str = "",
            provider: str = "unknown", reasoning: str = "unknown",
            sampling: str = "unknown", network: str = "unknown",
            configuration_evidence: str = "",
            comparison_track: str = "B_native_product",
            control_contract: dict | None = None) -> int:
    cdir = _resolve(case)
    if cdir is None:
        print(f"[错误] 找不到用例目录：{CASES}\\{case}*")
        return 2
    if not (cdir / "prompt.txt").is_file():
        print(f"[错误] 缺 prompt.txt：{cdir}")
        return 2
    if protocol_version not in {"hev-v2", CURRENT_PROTOCOL}:
        print(f"[错误] 未知运行协议：{protocol_version}")
        return 2
    if admission_track not in ADMISSION_TRACKS:
        print(f"[错误] 未知准入轨：{admission_track}")
        return 2
    if comparison_track not in COMPARISON_TRACKS:
        print(f"[错误] 未知比较轨：{comparison_track}")
        return 2
    control_contract = control_contract or {}
    contract_raw = json.dumps(control_contract, ensure_ascii=False, sort_keys=True).encode("utf-8")
    contract_sha256 = hashlib.sha256(contract_raw).hexdigest() if control_contract else ""
    config_evidence_path = Path(configuration_evidence).resolve() if configuration_evidence else None
    if config_evidence_path is not None and not config_evidence_path.is_file():
        print(f"[错误] 配置快照不存在：{config_evidence_path}")
        return 2

    root = Path(root) if root else TMP_ROOT
    work = root / cdir.name / product / f"run{run}" / "work"
    if work.parent.exists() and any(work.parent.iterdir()):
        print(f"[错误] 运行槽位已存在，禁止覆盖：{work.parent}")
        print(f"→ 请改用新的 --run 编号；每次真实运行必须保留独立 run_id。")
        return 3
    work.mkdir(parents=True, exist_ok=True)

    src = cdir / "inputs"
    n = 0
    if src.is_dir():
        for f in src.rglob("*"):
            if f.is_file():
                dst = work / f.relative_to(src)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)
                n += 1
        for f in src.rglob("*"):
            if f.is_file() and _sha8(f) != _sha8(work / f.relative_to(src)):
                print(f"[错误] 输入副本指纹不一致：{f}")
                return 3

    prompt = cdir / "prompt.txt"
    run_id = _new_run_id(cdir, product, run)
    evidence = work.parent / "evidence"
    for directory in (
        evidence,
        evidence / "session",
        evidence / "export-source",
        evidence / "original-artifacts",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    cfg = _product_config(product)
    prep = {
        "schema_version": RUN_SCHEMA_VERSION,
        "protocol_version": protocol_version,
        "admission_track": admission_track,
        "comparison_track": comparison_track,
        "control_contract": control_contract,
        "control_contract_sha256": contract_sha256,
        "record_type": "product_run",
        "run_id": run_id,
        "run_key": f"{cdir.name}__{product}__r{run}",
        "case": cdir.name,
        "product": product,
        "run": run,
        "variant": variant,
        "root": str(root),
        "work_dir": str(work),
        "evidence_dir": str(evidence),
        "started_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "prompt_sha8": _sha8(prompt),
        "inputs_sha8": {
            str(f.relative_to(src)): _sha8(f)
            for f in src.rglob("*") if f.is_file()
        } if src.is_dir() else {},
        "task_revision": _task_revision(cdir),
        "product_revision": _product_revision(product),
        "execution_context": {
            "product_version": product_version or cfg.get("version", "unknown"),
            "account": cfg.get("account", "unknown"),
            "model": model,
            "provider": provider,
            "reasoning": reasoning,
            "sampling": sampling,
            "tools": _csv_values(tools),
            "permissions": permissions,
            "network": network,
            "surface": surface,
            "context_policy": context_policy,
            "skills_state": skills_state,
            "memory_state": memory_state,
            "interface_precheck": interface_precheck,
            "configuration_evidence": str(config_evidence_path) if config_evidence_path else "",
            "configuration_evidence_sha256": _sha256(config_evidence_path) if config_evidence_path else "",
        },
    }
    _write_json(work.parent / "prepare.json", prep)
    _write_json(work.parent / "run.json",
                _run_skeleton(cdir, product, run, variant, root, work, prep))
    ver = prep["execution_context"]["product_version"]
    print(f"运行唯一 ID：{run_id}")
    print(f"工作目录已就绪：{work}（放入 {n} 个输入文件）")
    print(f"证据目录已就绪：{evidence}")
    print(f"产品配置：{product} version={ver} ｜ 如需更新，改 products/products.json")
    print(f"投喂指令：{prompt}  ｜ sha256[:8] = {_sha8(prompt)}")
    print(f"→ 新开 {product} 会话，把 prompt.txt 全文粘贴投喂；会话 / 外部日志 / 截图留痕。")
    print(f"→ 跑完后：python scripts/sbatch.py collect {case} {product} --run {run} --work \"{work}\"")
    return 0


RESULTS_PREAMBLE = (
    "# S 批跑测结果大表\n\n"
    "> 产物分 = checker 原始实得/满分；**归一分**按 `docs/03 §1.8`：`实得/满分 × 权重`"
    "（普通题 6、埋雷题 4）。行为分按 `spec.md` 观察格人工判定，逐条写证据引用。\n"
    "> 失败编码按 `docs/10` 两轴 `A_-B_`。\n\n"
)
RESULTS_HEADER = (
    "| 题 | 产品 | run | 产物分(实得/满分) | 归一分 | 行为分(普通0–4/埋雷0–6) | 单题合计(0–10) | "
    "checker exit | 跑测时间 | 备注 |\n"
    "|---|---|---|---|---|---|---|---|---|---|\n"
)


def results_row(case: str, product: str, run: int, got: float, full: float,
                exit_code: int, now: str, variant: str, run_id: str = "") -> str:
    """一行 = 10 列，必须与 RESULTS_HEADER 同宽。

    归一分/行为分/单题合计留给人工判定（空）；variant 落备注列。
    2026-10-25 前这里只有 8 列，导致整行右移、exit/时间/备注全部错列。
    """
    note = f"run_id={run_id} ｜ variant={variant}" if run_id else f"variant={variant}"
    return (f"| {case} | {product} | {run} | {got}/{full} | | | | "
            f"exit={exit_code} | {now} | {note} |\n")


def collect(case: str, product: str, run: int, work: str,
            interventions: int = 0, turns: int = 0,
            elapsed=None, timed_out: bool = False, rerun: bool = False,
            variant=None, termination: str = "product_declared_done",
            observed_cwd: str = "", cwd_evidence: str = "",
            observed_model: str = "", observed_provider: str = "",
            observed_reasoning: str = "", observed_sampling: str = "",
            observed_tools="", observed_permissions: str = "",
            observed_context_source: str = "",
            configuration_evidence: str = "",
            evidence_mode: str = "unverified", preflight_shot: str = "",
            completion_shot: str = "", session_export: str = "",
            recording: str = "", export_evidence: str = "") -> int:
    cdir = _resolve(case)
    if cdir is None:
        print(f"[错误] 找不到用例目录：{CASES}\\{case}*")
        return 2
    chk = cdir / "checker.py"
    if not chk.is_file():
        print(f"[错误] 缺 checker.py：{chk}")
        return 2

    w = Path(work)
    if not w.is_dir():
        print(f"[错误] 工作目录不存在：{w}")
        return 2

    out = SBATCH / cdir.name / product / f"run{run}"
    prep_path = w.parent / "prepare.json"
    if not prep_path.is_file():
        print("[错误] 缺运行前 prepare.json；拒绝归档。")
        return 3
    try:
        prep = json.loads(prep_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("[错误] prepare.json 无法解析；拒绝归档。")
        return 3
    if (prep.get("case") != cdir.name or prep.get("product") != product
            or prep.get("run") != run or not prep.get("run_id")
            or Path(prep.get("work_dir", "")).resolve() != w.resolve()):
        print("[错误] prepare 身份或工作目录与 collect 参数不一致；拒绝归档。")
        return 3
    run_src = w.parent / "run.json"
    if not run_src.is_file() or json.loads(run_src.read_text(encoding="utf-8")).get("run_id") != prep["run_id"]:
        print("[错误] 运行前 run.json 与 prepare 身份不一致；拒绝归档。")
        return 3
    protocol_version = prep.get("protocol_version", "hev-v2")
    if evidence_mode not in {"unverified", "native_trace", "desktop_export", "screen_recording"}:
        print("[错误] 未知证据模式。")
        return 3
    if observed_cwd and Path(observed_cwd).resolve() != w.resolve():
        print("[错误] 原生会话 cwd 与准备工作区不同；拒绝归档。")
        return 3
    if bool(observed_cwd) != bool(cwd_evidence):
        print("[错误] observed-cwd 与 cwd-evidence 必须同时提供。")
        return 3
    evidence_paths = {
        "cwd_evidence": cwd_evidence,
        "preflight_shot": preflight_shot,
        "completion_shot": completion_shot,
        "session_export": session_export,
        "recording": recording,
        "export_evidence": export_evidence,
        "configuration_evidence": configuration_evidence,
    }
    if any(value and not Path(value).is_file() for value in evidence_paths.values()):
        print("[错误] 指定的证据文件不存在；拒绝归档。")
        return 3
    if evidence_mode == "native_trace" and not (observed_cwd and cwd_evidence):
        print("[错误] 原生轨迹模式必须提供观察到的 cwd 和轨迹文件。")
        return 3
    if (evidence_mode == "native_trace" and protocol_version == CURRENT_PROTOCOL
            and not session_export):
        print("[错误] v3 原生轨迹模式必须保存完整会话日志。")
        return 3
    if evidence_mode == "desktop_export" and not all(
        (preflight_shot, completion_shot, session_export, export_evidence)
    ):
        print("[错误] 桌面导出模式必须提供发送前截图、完成截图、会话日志原件和导出来源证据。")
        return 3
    if evidence_mode == "screen_recording" and not all((preflight_shot, recording, export_evidence)):
        print("[错误] 录屏模式必须提供发送前截图、全程录像和导出来源证据。")
        return 3
    if out.exists() and any(out.iterdir()):
        print(f"[错误] 收件槽位已存在，禁止覆盖：{out}")
        return 3
    art = out / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    for f in w.rglob("*"):
        if f.is_file():
            dst = art / f.relative_to(w)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
    n_art = sum(1 for f in art.rglob("*") if f.is_file())
    artifact_hashes = {f.relative_to(art).as_posix(): _sha256(f)
                       for f in art.rglob("*") if f.is_file()}
    archived_evidence = {}
    for key, value in evidence_paths.items():
        if not value:
            continue
        source = Path(value).resolve()
        destination = out / "evidence" / key / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        archived_evidence[key] = {
            "path": str(destination.resolve()),
            "source_path": str(source),
            "sha256": _sha256(destination),
        }

    pr = subprocess.run([sys.executable, "-X", "utf8", str(chk), str(art)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    (out / "checker_output.txt").write_text(pr.stdout or "", encoding="utf-8")

    m = re.search(r"合计[：:]\s*([\d.]+)\s*/\s*([\d.]+)", pr.stdout or "")
    got, full = (m.group(1), m.group(2)) if m else ("?", "?")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    metrics = {}
    mm = re.search(r"METRICS_JSON:\s*(\{.*\})\s*$", pr.stdout or "", re.MULTILINE)
    if mm:
        try:
            metrics = json.loads(mm.group(1))
        except json.JSONDecodeError:
            metrics = {}

    shutil.copy2(prep_path, out / "prepare.json")
    variant = variant or prep.get("variant", "default")
    run_id = prep.get("run_id")
    if not run_id:
        print("[错误] prepare.json 缺 run_id；该现场不能作为新制式运行归档。")
        return 3
    started_at = prep.get("started_at") or now
    ended_at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    if elapsed is None:
        try:
            elapsed = (datetime.datetime.now().astimezone()
                       - datetime.datetime.fromisoformat(started_at)).total_seconds()
        except (TypeError, ValueError):
            elapsed = None

    _write_json(out / "manifest.json", {
        "schema_version": prep.get("schema_version", RUN_SCHEMA_VERSION),
        "protocol_version": protocol_version,
        "admission_track": prep.get("admission_track", "product_result"),
        "comparison_track": prep.get("comparison_track", "B_native_product"),
        "control_contract_sha256": prep.get("control_contract_sha256", ""),
        "record_type": "product_run",
        "run_id": run_id,
        "case": cdir.name,
        "product": product,
        "run": run,
        "variant": variant,
        "root": prep.get("root", ""),
        "work_dir": str(w),
        "product_revision": _product_revision(product),
        "started_at": started_at,
        "ended_at": ended_at,
        "prompt_sha8": prep.get("prompt_sha8") or _sha8(cdir / "prompt.txt"),
        "inputs_sha8": prep.get("inputs_sha8", {}),
        "artifacts_count": n_art,
        "artifacts_sha256": artifact_hashes,
        "evidence": archived_evidence,
        "checker_exit": pr.returncode,
        "interventions": interventions,
        "rerun": rerun,
        "task_revision": prep.get("task_revision") or _task_revision(cdir),
        "execution_context": prep.get("execution_context", {}),
    })
    _write_json(out / "usage.json", {
        "elapsed_seconds": round(elapsed, 1) if elapsed is not None else None,
        "turns": turns,
        "timed_out": timed_out,
        "manual_interventions": interventions,
    })
    raw_got = _num(got)
    raw_full = _num(full)
    score_status = "timeout" if timed_out else ("error" if termination == "error" else "graded")
    _write_json(out / "score.json", {
        "raw_got": raw_got,
        "raw_full": raw_full,
        "metrics": metrics,
        "failure_code": "",
        "evidence_grade": "",
        "status": score_status,
    })

    # v3 沿用 v2 运行记录主体，并增加协议、准入轨与分层证据范围。
    run_src = w.parent / "run.json"
    if run_src.is_file():
        run_doc = json.loads(run_src.read_text(encoding="utf-8"))
    else:
        run_doc = _run_skeleton(cdir, product, run, variant,
                                Path(prep.get("root") or w.parent), w, prep)
    artifact_norm = None
    if isinstance(raw_got, (int, float)) and isinstance(raw_full, (int, float)) and raw_full > 0:
        artifact_norm = round(raw_got / raw_full, 4)
    if termination == "error":
        success = None
    elif timed_out:
        success = 0
    else:
        success = 1 if (pr.returncode == 0 and artifact_norm == 1.0) else 0
    run_doc.update({
        "schema_version": prep.get("schema_version", RUN_SCHEMA_VERSION),
        "protocol_version": protocol_version,
        "admission_track": prep.get("admission_track", "product_result"),
        "comparison_track": prep.get("comparison_track", "B_native_product"),
        "control_contract": prep.get("control_contract", {}),
        "control_contract_sha256": prep.get("control_contract_sha256", ""),
        "record_type": "product_run",
        "run_id": run_id,
        "run_key": f"{cdir.name}__{product}__r{run}",
        "variant": variant,
        "status": "timeout" if timed_out else ("error" if termination == "error" else "scored"),
        "environment": {
            "root": prep.get("root", ""),
            "work_dir": str(w),
        },
        "execution_context": prep.get("execution_context", run_doc.get("execution_context", {})),
        "execution_context_observed": {
            "model": observed_model,
            "provider": observed_provider,
            "reasoning": observed_reasoning,
            "sampling": observed_sampling,
            "tools": _csv_values(observed_tools),
            "permissions": observed_permissions,
            "source": observed_context_source,
        },
        "collection_verification": {
            "prepared_work_match": True,
            "mode": evidence_mode,
            "claim_scope": {
                "native_trace": "execution_behavior",
                "screen_recording": "visible_actions_only",
                "desktop_export": "product_result",
            }.get(evidence_mode, "unverified"),
            "observed_cwd_match": bool(observed_cwd),
            "evidence": archived_evidence,
            "screen_recording_scope": "visible_actions_only" if evidence_mode == "screen_recording" else "",
        },
        "termination": {
            "reason": "timeout" if timed_out else termination,
            "timed_out": timed_out,
            "turns": turns,
            "manual_interventions": interventions,
        },
        "evaluation": {
            "reward_basis": run_doc.get("evaluation", {}).get("reward_basis", []),
            "components": {"artifact": artifact_norm},
            "success": success,
            "v1": run_doc.get("evaluation", {}).get("v1"),
        },
        "evidence": {
            "run_dir": str(out),
            "timeline": str(out / "timeline.md") if (out / "timeline.md").is_file() else "",
            "session_log": archived_evidence.get("session_export", {}).get("path", ""),
            "artifacts": str(art),
            "shots": str(out / "shots") if (out / "shots").exists() else "",
            "recording": archived_evidence.get("recording", {}).get("path", ""),
        },
    })
    _write_json(out / "run.json", run_doc)

    SBATCH.mkdir(parents=True, exist_ok=True)
    res = SBATCH / "results.md"
    if not res.exists():
        res.write_text(RESULTS_PREAMBLE + RESULTS_HEADER, encoding="utf-8")

    res.write_text(res.read_text(encoding="utf-8")
                   + results_row(cdir.name, product, run, got, full,
                                 pr.returncode, now, variant, run_id),
                   encoding="utf-8")

    print(f"产物已归档：{art}")
    print(f"checker 输出：{out / 'checker_output.txt'}")
    print(f"证据三件套：manifest.json / usage.json / score.json → {out}")
    print(f"运行唯一 ID：{run_id}")
    print(f"产物分：{got}/{full}（exit={pr.returncode}）→ 已记入 {res}")
    return 0


def _eligibility(run_doc: dict) -> tuple[bool, list[str]]:
    adj = run_doc.get("adjudication", {})
    reasons = []
    labels = {
        "rules_frozen": "规则未冻结",
        "task_valid": "题面无效或未核验",
        "evidence_valid": "证据无效或未核验",
        "uncontaminated": "运行受污染或未核验",
    }
    for key, label in labels.items():
        if adj.get(key) != "yes":
            reasons.append(label)
    ruling = adj.get("final_ruling", "pending")
    if ruling not in {"pass", "fail"}:
        reasons.append(f"终裁={ruling}，不可进入正式比较")
    grade = run_doc.get("diagnostics", {}).get("evidence_grade", "")
    if grade not in {"A", "B", "C"}:
        reasons.append("证据等级未登记为 A/B/C")
    ctx = run_doc.get("execution_context", {})
    if run_doc.get("schema_version", 1) < 2:
        reasons.append("legacy 运行缺 v2 全量上下文，不可追认正式样本")
    if not run_doc.get("binding", {}).get("task_revision", "").startswith("sha256:"):
        reasons.append("缺单题 task_revision")
    if not ctx.get("product_version"):
        reasons.append("缺产品版本快照")
    if ctx.get("interface_precheck") not in {"passed", "not_applicable"}:
        reasons.append("接口预检未通过或未登记")
    verification = run_doc.get("collection_verification")
    if verification is not None:
        protocol_version = run_doc.get("protocol_version", "hev-v2")
        admission_track = run_doc.get("admission_track", "product_result")
        if admission_track not in ADMISSION_TRACKS:
            reasons.append("准入轨未登记")
        mode = verification.get("mode", "native_trace" if verification.get("observed_cwd_match") else "unverified")
        evidence = verification.get("evidence", {})
        if mode == "native_trace" and not verification.get("observed_cwd_match"):
            reasons.append("原生 cwd 未核验")
        elif (mode == "native_trace" and protocol_version == CURRENT_PROTOCOL
              and not evidence.get("session_export")):
            reasons.append("v3 原生会话日志缺失")
        elif mode == "desktop_export" and not all(
            evidence.get(key) for key in (
                "preflight_shot", "completion_shot", "session_export", "export_evidence"
            )
        ):
            reasons.append("桌面导出证据链不完整")
        elif mode == "desktop_export" and admission_track != "product_result":
            reasons.append("桌面导出模式只支持产品结果轨")
        elif mode == "screen_recording" and not all(
            evidence.get(key) for key in ("preflight_shot", "recording", "export_evidence")
        ):
            reasons.append("录屏证据链不完整")
        elif mode not in {"native_trace", "desktop_export", "screen_recording"}:
            reasons.append("运行过程证据模式未核验")
    if run_doc.get("product") == "codex":
        if ctx.get("memory_state") != "disabled":
            reasons.append("Codex Memory 未证实关闭")
        if ctx.get("skills_state") != "disabled":
            reasons.append("Codex Skills 未证实关闭")
    return not reasons, reasons


def _causal_readiness(run_doc: dict) -> tuple[bool, list[str]]:
    """判断单场是否具备进入 Harness 因果配对的必要控制信息。

    真正的 causal_eligible 还要求同题 Codex/DSH 两场正式准入且合同哈希相同，
    由 formal_report 在批次层完成配对判断。
    """
    reasons = []
    if run_doc.get("comparison_track") != "A_same_model_cli":
        return False, ["非 A_same_model_cli 轨，只能作整体产品观察"]
    if run_doc.get("admission_track") != "execution_behavior":
        reasons.append("同模型 Harness 轨必须进入执行行为准入轨")
    ctx = run_doc.get("execution_context", {})
    if ctx.get("surface") != "cli":
        reasons.append("同模型 Harness 轨只接受 CLI 表面")
    product = run_doc.get("product")
    if product not in {"codex", "dsh"}:
        reasons.append("同模型 Harness 轨只接受 Codex/DSH")
    expected_policy = {"codex": "isolated_codex_home", "dsh": "headless_new_agent"}.get(product)
    if expected_policy and ctx.get("context_policy") != expected_policy:
        reasons.append(f"{product} 上下文隔离策略不符合 A 轨")
    if run_doc.get("collection_verification", {}).get("mode") != "native_trace":
        reasons.append("同模型 Harness 轨必须保留 CLI 原生轨迹")
    contract = run_doc.get("control_contract", {})
    observed = run_doc.get("execution_context_observed", {})
    required = (
        "contract_id", "only_variable", "model", "provider", "reasoning",
        "sampling", "environment_id", "network", "skills", "memory", "permissions",
        "harness_components",
    )
    for key in required:
        value = contract.get(key)
        if value is None or value == "" or (
            isinstance(value, str) and value in {"unknown", "REPLACE_ME"}
        ):
            reasons.append(f"控制合同缺 {key}")
    if contract.get("only_variable") != "harness":
        reasons.append("控制合同唯一改动不是 harness")
    if contract.get("provider") != "openai":
        reasons.append("当前 A 轨只接受隔离 Codex CLI 的内置 openai provider")
    if contract.get("sampling") != "provider_default":
        reasons.append("当前 A 轨只接受双方均未覆盖采样参数的 provider_default")
    if contract.get("network") not in {"blocked_externally", "not_used_and_trace_verified"}:
        reasons.append("网络控制只接受 blocked_externally/not_used_and_trace_verified")
    components = contract.get("harness_components", [])
    if not isinstance(components, list) or not HARNESS_TREATMENT_COMPONENTS.issubset(set(components)):
        reasons.append("Harness treatment 未覆盖 system_prompt/toolset/orchestration/context_management/stop_policy")
    if contract.get("skills") != "disabled":
        reasons.append("Skills 未冻结为 disabled")
    if contract.get("memory") != "disabled":
        reasons.append("Memory 未冻结为 disabled")
    actual_pairs = {
        "network": ctx.get("network"),
        "skills": ctx.get("skills_state"),
        "memory": ctx.get("memory_state"),
    }
    for key, actual in actual_pairs.items():
        if contract.get(key) != actual:
            reasons.append(f"实际 {key} 与控制合同不一致")
    if not observed.get("source"):
        reasons.append("缺模型/服务方运行时观察来源")
    for key in ("model", "provider", "reasoning", "sampling", "permissions"):
        if observed.get(key) != contract.get(key):
            reasons.append(f"运行时 {key} 与控制合同不一致")
    if not observed.get("tools"):
        reasons.append("未从命令/原生请求头记录该 Harness 的实际工具集")
    config_record = run_doc.get("collection_verification", {}).get("evidence", {}).get(
        "configuration_evidence", {}
    )
    if not ctx.get("configuration_evidence_sha256") or not config_record:
        reasons.append("缺单场配置快照归档")
    elif ctx.get("configuration_evidence_sha256") != config_record.get("sha256"):
        reasons.append("配置快照归档哈希与 prepare 不一致")
    if not run_doc.get("control_contract_sha256"):
        reasons.append("缺控制合同哈希")
    return not reasons, reasons


def adjudicate(case: str, product: str, run: int, *, evidence_grade: str,
               final_ruling: str, rules_frozen: str, task_valid: str,
               evidence_valid: str, uncontaminated: str,
               adjudicator: str, notes: str = "") -> int:
    cdir = _resolve(case)
    if cdir is None:
        print(f"[错误] 找不到用例目录：{CASES}\\{case}*")
        return 2
    run_path = SBATCH / cdir.name / product / f"run{run}" / "run.json"
    score_path = run_path.parent / "score.json"
    if not run_path.is_file():
        print(f"[错误] 缺 run.json：{run_path}")
        return 2
    doc = json.loads(run_path.read_text(encoding="utf-8"))
    doc.setdefault("diagnostics", {})["evidence_grade"] = evidence_grade
    doc["adjudication"] = {
        "rules_frozen": rules_frozen,
        "task_valid": task_valid,
        "evidence_valid": evidence_valid,
        "uncontaminated": uncontaminated,
        "final_ruling": final_ruling,
        "official_eligible": False,
        "exclusion_reasons": [],
        "adjudicator": adjudicator,
        "adjudicated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "notes": notes,
    }
    eligible, reasons = _eligibility(doc)
    causal_ready, causal_reasons = _causal_readiness(doc)
    doc["adjudication"]["official_eligible"] = eligible
    doc["adjudication"]["exclusion_reasons"] = reasons
    doc["adjudication"]["causal_ready"] = eligible and causal_ready
    doc["adjudication"]["causal_pair_status"] = (
        "pending_formal_report" if eligible and causal_ready else "not_ready"
    )
    doc["adjudication"].pop("causal_eligible", None)
    doc["adjudication"]["causal_exclusion_reasons"] = causal_reasons
    if final_ruling in {"unknown", "invalid", "not_applicable"}:
        doc.setdefault("evaluation", {})["success"] = None
    _write_json(run_path, doc)
    if score_path.is_file():
        score = json.loads(score_path.read_text(encoding="utf-8"))
        score["evidence_grade"] = evidence_grade
        score["final_ruling"] = final_ruling
        score["official_eligible"] = eligible
        _write_json(score_path, score)
    print(f"终裁完成：{doc.get('run_id', '')} ｜ official_eligible={eligible}")
    for reason in reasons:
        print(f"- 排除：{reason}")
    return 0


def formal_report() -> int:
    """只汇总规则冻结、题面有效、证据有效且无污染的产品运行。"""
    included = []
    excluded = []
    for path in sorted(SBATCH.glob("S*/**/run*/run.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if doc.get("record_type", "product_run") != "product_run":
            continue
        eligible, reasons = _eligibility(doc)
        causal_ready, causal_reasons = _causal_readiness(doc)
        row = {
            "run_id": doc.get("run_id", ""),
            "task": doc.get("task", ""),
            "product": doc.get("product", ""),
            "trial": doc.get("trial"),
            "final_ruling": doc.get("adjudication", {}).get("final_ruling", "pending"),
            "evidence_grade": doc.get("diagnostics", {}).get("evidence_grade", ""),
            "admission_track": doc.get("admission_track", "product_result"),
            "evidence_mode": doc.get("collection_verification", {}).get("mode", "unverified"),
            "comparison_track": doc.get("comparison_track", "B_native_product"),
            "control_contract_sha256": doc.get("control_contract_sha256", ""),
            "task_revision": doc.get("binding", {}).get("task_revision", ""),
            "causal_ready": eligible and causal_ready,
            "causal_eligible": False,
            "causal_reasons": causal_reasons,
            "reasons": reasons,
        }
        (included if eligible else excluded).append(row)
    causal_groups = {}
    for row in included:
        if not row["causal_ready"]:
            continue
        key = (row["task"], row["task_revision"], row["control_contract_sha256"])
        causal_groups.setdefault(key, []).append(row)
    causal_pairs = []
    for (task, task_revision, contract_sha), rows in causal_groups.items():
        products = {row["product"] for row in rows}
        paired = {"codex", "dsh"}.issubset(products)
        if paired:
            for row in rows:
                if row["product"] in {"codex", "dsh"}:
                    row["causal_eligible"] = True
                    row["causal_reasons"] = []
            causal_pairs.append({
                "task": task,
                "task_revision": task_revision,
                "control_contract_sha256": contract_sha,
                "products": sorted(products & {"codex", "dsh"}),
            })
        else:
            for row in rows:
                row["causal_reasons"] = ["缺同题、同控制合同的 Codex/DSH 正式配对"]
    report = {
        "schema_version": 1,
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "policy": "仅纳入规则冻结、题面有效、证据有效、无污染且终裁为 pass/fail 的 product_run。",
        "included": included,
        "excluded": excluded,
        "causal_pairs": causal_pairs,
    }
    _write_json(SBATCH / "formal-results.json", report)
    lines = [
        "# 正式比较准入表", "",
        "> 只纳入规则冻结、题面有效、证据有效、无污染且终裁为 pass/fail 的产品运行。", "",
        f"纳入 **{len(included)}**；排除/待裁 **{len(excluded)}**。", "",
        "| run_id | 题 | 产品 | run | 比较轨 | 准入轨 | 证据模式 | Harness因果 | 终裁 | 证据等级 |",
        "|---|---|---|---:|---|---|---|---|---|---|",
    ]
    for row in included:
        lines.append(
            f"| {row['run_id']} | {row['task']} | {row['product']} | {row['trial']} | "
            f"{row['comparison_track']} | {row['admission_track']} | {row['evidence_mode']} | "
            f"{'yes' if row['causal_eligible'] else 'no'} | "
            f"{row['final_ruling']} | {row['evidence_grade']} |"
        )
    lines += ["", "## 排除与待裁", "", "| run_id | 题/产品 | 原因 |", "|---|---|---|"]
    for row in excluded:
        reason = "；".join(row["reasons"]) or "未登记"
        lines.append(f"| {row['run_id']} | {row['task']} / {row['product']} | {reason} |")
    (SBATCH / "formal-results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"正式比较：纳入 {len(included)}，排除/待裁 {len(excluded)}")
    return 0


def summary(case: str, run: int = 1) -> int:
    """汇总试点五款 score.json / run.json，写 pilot-results.json 与 pilot-summary.md。"""
    cdir = _resolve(case)
    if cdir is None:
        print(f"[错误] 找不到用例目录：{CASES}\\{case}*")
        return 2
    root = SBATCH / cdir.name
    rows = []
    for p in PRODUCTS:
        d = root / p / f"run{run}"
        if not d.is_dir():
            rows.append({"product": p, "status": "missing", "raw_got": None,
                         "raw_full": None, "success": None, "v1": None,
                         "failure_code": ""})
            continue
        score = {}
        run_doc = {}
        sp = d / "score.json"
        rp = d / "run.json"
        if sp.is_file():
            score = json.loads(sp.read_text(encoding="utf-8"))
        if rp.is_file():
            run_doc = json.loads(rp.read_text(encoding="utf-8"))
        rows.append({
            "product": p,
            "status": run_doc.get("status") or score.get("status", "missing"),
            "raw_got": score.get("raw_got"),
            "raw_full": score.get("raw_full"),
            "success": run_doc.get("evaluation", {}).get("success"),
            "v1": run_doc.get("evaluation", {}).get("v1"),
            "failure_code": run_doc.get("diagnostics", {}).get("failure_code", ""),
        })

    found = sum(1 for r in rows if r["status"] != "missing")
    result = {
        "suite": SUITE,
        "task": cdir.name,
        "trial": run,
        "scope": "pilot",
        "official": False,
        "coverage": {"expected": len(PRODUCTS), "found": found,
                     "missing": len(PRODUCTS) - found},
        "by_product": {r["product"]: r for r in rows},
        "notes": "管线试点，不作五款排名；success 仅由 checker 产物分推导，行为分另见 grade.yaml。",
    }
    root.mkdir(parents=True, exist_ok=True)
    _write_json(root / "pilot-results.json", result)

    lines = [
        f"# {cdir.name} · S06 管线试点汇总",
        "",
        "> 试点只验证流程与证据完整性，**不作五款排名**。",
        f"> 覆盖：{found}/{len(PRODUCTS)}；success 仅由 checker 产物分推导，行为分另见 `grade.yaml`。",
        "",
        "| 产品 | status | 产物分 | success | v1 | failure_code |",
        "|---|---|---:|---:|---:|---|",
    ]
    for r in rows:
        got = "—" if r["raw_got"] is None else r["raw_got"]
        full = "—" if r["raw_full"] is None else r["raw_full"]
        succ = "—" if r["success"] is None else r["success"]
        v1 = "—" if r["v1"] is None else r["v1"]
        lines.append(f"| {r['product']} | {r['status']} | {got}/{full} | {succ} | {v1} | {r['failure_code']} |")
    (root / "pilot-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"覆盖：{found}/{len(PRODUCTS)}")
    print(f"汇总：{root / 'pilot-results.json'}")
    print(f"报告：{root / 'pilot-summary.md'}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="S 批跑测脚手架")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("prepare", help="准备一次运行（建工作目录、放 inputs）")
    p1.add_argument("case")
    p1.add_argument("product", choices=PRODUCTS)
    p1.add_argument("--run", type=int, default=1)
    p1.add_argument("--root", default=None, help="工作区根目录；缺省用 C:\\tmp_run")
    p1.add_argument("--variant", default="default", help="配置变体：default / path-hint / swap-P3 ...")
    p1.add_argument("--model", default="unknown", help="本次实际模型；未知必须显式保留 unknown")
    p1.add_argument("--provider", default="unknown", help="模型服务来源；同模型对照必须冻结")
    p1.add_argument("--reasoning", default="unknown", help="推理档位/预算；同模型对照必须冻结")
    p1.add_argument("--sampling", default="unknown", help="采样参数摘要；同模型对照必须冻结")
    p1.add_argument("--tools", default="", help="启用工具，逗号分隔；无则留空")
    p1.add_argument("--permissions", default="unknown", help="权限/沙箱策略快照")
    p1.add_argument("--network", default="unknown", help="网络策略；同模型对照必须冻结")
    p1.add_argument("--surface", default="desktop", choices=["cli", "desktop", "web"],
                    help="实际产品表面；同一产品的 CLI 与桌面端必须分开登记")
    p1.add_argument("--context-policy", default="default",
                    help="上下文隔离策略；CLI runner 记录 isolated_codex_home/headless_new_agent")
    p1.add_argument("--product-version", default="",
                    help="覆盖产品登记表中的批次实测版本")
    p1.add_argument("--configuration-evidence", default="",
                    help="本产品冻结配置快照原件；A_same_model_cli 必填")
    p1.add_argument("--skills-state", default="unknown",
                    choices=["enabled", "disabled", "unknown", "not_applicable"])
    p1.add_argument("--memory-state", default="unknown",
                    choices=["enabled", "disabled", "unknown", "not_applicable"])
    p1.add_argument("--interface-precheck", default="not_run",
                    choices=["passed", "failed", "not_run", "not_applicable"])
    p1.add_argument("--protocol-version", default=CURRENT_PROTOCOL,
                    choices=["hev-v2", CURRENT_PROTOCOL],
                    help="新运行默认使用 hev-v3；hev-v2 仅供复现旧制式")
    p1.add_argument("--admission-track", default="product_result",
                    choices=sorted(ADMISSION_TRACKS),
                    help="产品结果轨或执行行为轨")
    p1.add_argument("--comparison-track", default="B_native_product",
                    choices=sorted(COMPARISON_TRACKS),
                    help="同模型 CLI、原生整体产品或机制换件轨")
    p1.add_argument("--control-contract", default="",
                    help="A_same_model_cli/M_mechanism 使用的冻结控制合同 JSON")

    p2 = sub.add_parser("collect", help="归档产物并判分，写入结果表与证据三件套")
    p2.add_argument("case")
    p2.add_argument("product", choices=PRODUCTS)
    p2.add_argument("--run", type=int, default=1)
    p2.add_argument("--work", required=True)
    p2.add_argument("--observed-cwd", default="", help="原生会话中观察到的绝对 cwd")
    p2.add_argument("--cwd-evidence", default="", help="可复核 cwd 的原生日志或记录文件")
    p2.add_argument("--observed-model", default="", help="原生轨迹或固定命令观察到的实际模型")
    p2.add_argument("--observed-provider", default="", help="原生轨迹或隔离配置观察到的服务方")
    p2.add_argument("--observed-reasoning", default="", help="原生请求头或固定命令观察到的推理档位")
    p2.add_argument("--observed-sampling", default="", help="原生请求头或固定命令观察到的采样策略")
    p2.add_argument("--observed-tools", default="", help="原生请求头或冻结启动配置观察到的工具集")
    p2.add_argument("--observed-permissions", default="", help="原生权限事件或固定启动命令观察到的权限策略")
    p2.add_argument("--observed-context-source", default="", help="模型/服务方观察值的证据来源说明")
    p2.add_argument("--evidence-mode", default="unverified",
                    choices=["unverified", "native_trace", "desktop_export", "screen_recording"])
    p2.add_argument("--preflight-shot", default="", help="发送前截图")
    p2.add_argument("--completion-shot", default="", help="产品完成后的最终状态截图")
    p2.add_argument("--session-export", default="", help="原始会话日志、轨迹或产品导出记录")
    p2.add_argument("--recording", default="", help="可选全程录像；仅旧 screen_recording 模式必需")
    p2.add_argument("--export-evidence", default="", help="日志/产物导出来源与落点证据")
    p2.add_argument("--configuration-evidence", default="", help="与 prepare 相同的冻结配置快照原件")
    p2.add_argument("--interventions", type=int, default=0, help="人工干预次数")
    p2.add_argument("--turns", type=int, default=0, help="会话轮次")
    p2.add_argument("--elapsed", type=float, default=None, help="墙钟秒数；缺省按 prepare 时间戳推算")
    p2.add_argument("--timed-out", action="store_true", help="超时终止（二值失败事件）")
    p2.add_argument("--rerun", action="store_true", help="是否为重跑")
    p2.add_argument("--variant", default=None, help="覆盖 prepare.json 中的 variant")
    p2.add_argument("--termination", default="product_declared_done",
                    choices=["product_declared_done", "timeout", "error", "manual_stop"],
                    help="终止原因；error 会从成功率分母剔除")

    p3 = sub.add_parser("summary", help="汇总试点五款 score.json / run.json")
    p3.add_argument("case")
    p3.add_argument("--run", type=int, default=1)

    p4 = sub.add_parser("adjudicate", help="人工终裁并计算正式比较准入资格")
    p4.add_argument("case")
    p4.add_argument("product", choices=PRODUCTS)
    p4.add_argument("--run", type=int, default=1)
    p4.add_argument("--evidence-grade", required=True, choices=["A", "B", "C", "N"])
    p4.add_argument("--final-ruling", required=True,
                    choices=["pass", "fail", "unknown", "invalid", "not_applicable"])
    for flag in ("rules-frozen", "task-valid", "evidence-valid", "uncontaminated"):
        p4.add_argument(f"--{flag}", required=True, choices=["yes", "no", "unknown"])
    p4.add_argument("--adjudicator", required=True)
    p4.add_argument("--notes", default="")

    sub.add_parser("formal-report", help="生成仅含合格运行的正式比较准入表")

    a = ap.parse_args()
    if a.cmd == "prepare":
        control_contract = {}
        if a.control_contract:
            try:
                control_contract = json.loads(Path(a.control_contract).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"[错误] 控制合同无法读取：{exc}")
                sys.exit(2)
        sys.exit(prepare(a.case, a.product, a.run,
                         root=a.root, variant=a.variant, model=a.model,
                         tools=a.tools, permissions=a.permissions,
                         skills_state=a.skills_state, memory_state=a.memory_state,
                         interface_precheck=a.interface_precheck,
                         protocol_version=a.protocol_version,
                         admission_track=a.admission_track,
                         surface=a.surface, context_policy=a.context_policy,
                         product_version=a.product_version,
                         provider=a.provider, reasoning=a.reasoning,
                         sampling=a.sampling, network=a.network,
                         configuration_evidence=a.configuration_evidence,
                         comparison_track=a.comparison_track,
                         control_contract=control_contract))
    elif a.cmd == "summary":
        sys.exit(summary(a.case, a.run))
    elif a.cmd == "adjudicate":
        sys.exit(adjudicate(
            a.case, a.product, a.run,
            evidence_grade=a.evidence_grade,
            final_ruling=a.final_ruling,
            rules_frozen=a.rules_frozen,
            task_valid=a.task_valid,
            evidence_valid=a.evidence_valid,
            uncontaminated=a.uncontaminated,
            adjudicator=a.adjudicator,
            notes=a.notes,
        ))
    elif a.cmd == "formal-report":
        sys.exit(formal_report())
    else:
        sys.exit(collect(a.case, a.product, a.run, a.work,
                         interventions=a.interventions, turns=a.turns,
                         elapsed=a.elapsed, timed_out=a.timed_out, rerun=a.rerun,
                         variant=a.variant, termination=a.termination,
                         observed_cwd=a.observed_cwd, cwd_evidence=a.cwd_evidence,
                         observed_model=a.observed_model, observed_provider=a.observed_provider,
                         observed_reasoning=a.observed_reasoning,
                         observed_sampling=a.observed_sampling,
                         observed_tools=a.observed_tools,
                         observed_permissions=a.observed_permissions,
                         observed_context_source=a.observed_context_source,
                         evidence_mode=a.evidence_mode, preflight_shot=a.preflight_shot,
                         completion_shot=a.completion_shot,
                         session_export=a.session_export,
                         recording=a.recording, export_evidence=a.export_evidence,
                         configuration_evidence=a.configuration_evidence))


if __name__ == "__main__":
    main()
