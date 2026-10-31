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
PINS = REPO / "benchmarks" / "pins.json"
PRODUCTS_REGISTRY = REPO / "products" / "products.json"
TASK_REVISION_FILES = {"task.md", "prompt.txt", "checker.py", "spec.md", "truth.json"}


def _sha8(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:8]


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
        "schema_version": 2,
        "record_type": "product_run",
        "run_id": run_id,
        "run_key": f"{cdir.name}__{product}__r{run}",
        "suite": SUITE,
        "task": cdir.name,
        "product": product,
        "trial": run,
        "variant": variant,
        "status": "prepared",
        "environment": {"root": str(root), "work_dir": str(work)},
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
            interface_precheck: str = "not_run") -> int:
    cdir = _resolve(case)
    if cdir is None:
        print(f"[错误] 找不到用例目录：{CASES}\\{case}*")
        return 2
    if not (cdir / "prompt.txt").is_file():
        print(f"[错误] 缺 prompt.txt：{cdir}")
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

    prompt = cdir / "prompt.txt"
    run_id = _new_run_id(cdir, product, run)
    cfg = _product_config(product)
    prep = {
        "schema_version": 2,
        "record_type": "product_run",
        "run_id": run_id,
        "run_key": f"{cdir.name}__{product}__r{run}",
        "case": cdir.name,
        "product": product,
        "run": run,
        "variant": variant,
        "root": str(root),
        "work_dir": str(work),
        "started_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "prompt_sha8": _sha8(prompt),
        "inputs_sha8": {
            str(f.relative_to(src)): _sha8(f)
            for f in src.rglob("*") if f.is_file()
        } if src.is_dir() else {},
        "task_revision": _task_revision(cdir),
        "product_revision": _product_revision(product),
        "execution_context": {
            "product_version": cfg.get("version", "unknown"),
            "account": cfg.get("account", "unknown"),
            "model": model,
            "tools": _csv_values(tools),
            "permissions": permissions,
            "skills_state": skills_state,
            "memory_state": memory_state,
            "interface_precheck": interface_precheck,
        },
    }
    _write_json(work.parent / "prepare.json", prep)
    _write_json(work.parent / "run.json",
                _run_skeleton(cdir, product, run, variant, root, work, prep))
    ver = cfg.get("version", "未登记")
    print(f"运行唯一 ID：{run_id}")
    print(f"工作目录已就绪：{work}（放入 {n} 个输入文件）")
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
            variant=None, termination: str = "product_declared_done") -> int:
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
    art = out / "artifacts"
    if art.exists():
        shutil.rmtree(art)
    art.mkdir(parents=True, exist_ok=True)
    for f in w.rglob("*"):
        if f.is_file():
            dst = art / f.relative_to(w)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
    n_art = sum(1 for f in art.rglob("*") if f.is_file())

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

    prep_path = w.parent / "prepare.json"
    prep = json.loads(prep_path.read_text(encoding="utf-8")) if prep_path.is_file() else {}
    if prep_path.is_file():
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
        "schema_version": 2,
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

    # v2 运行记录：与 docs/14 的 run.json 对齐
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
        "schema_version": 2,
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
            "session_log": str(out / "session.log") if (out / "session.log").exists() else "",
            "artifacts": str(art),
            "shots": str(out / "shots") if (out / "shots").exists() else "",
            "recording": str(out / "recording.txt") if (out / "recording.txt").is_file() else "",
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
    if run_doc.get("product") == "codex":
        if ctx.get("memory_state") != "disabled":
            reasons.append("Codex Memory 未证实关闭")
        if ctx.get("skills_state") != "disabled":
            reasons.append("Codex Skills 未证实关闭")
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
    doc["adjudication"]["official_eligible"] = eligible
    doc["adjudication"]["exclusion_reasons"] = reasons
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
        row = {
            "run_id": doc.get("run_id", ""),
            "task": doc.get("task", ""),
            "product": doc.get("product", ""),
            "trial": doc.get("trial"),
            "final_ruling": doc.get("adjudication", {}).get("final_ruling", "pending"),
            "evidence_grade": doc.get("diagnostics", {}).get("evidence_grade", ""),
            "reasons": reasons,
        }
        (included if eligible else excluded).append(row)
    report = {
        "schema_version": 1,
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "policy": "仅纳入规则冻结、题面有效、证据有效、无污染且终裁为 pass/fail 的 product_run。",
        "included": included,
        "excluded": excluded,
    }
    _write_json(SBATCH / "formal-results.json", report)
    lines = [
        "# 正式比较准入表", "",
        "> 只纳入规则冻结、题面有效、证据有效、无污染且终裁为 pass/fail 的产品运行。", "",
        f"纳入 **{len(included)}**；排除/待裁 **{len(excluded)}**。", "",
        "| run_id | 题 | 产品 | run | 终裁 | 证据等级 |", "|---|---|---|---:|---|---|",
    ]
    for row in included:
        lines.append(f"| {row['run_id']} | {row['task']} | {row['product']} | {row['trial']} | {row['final_ruling']} | {row['evidence_grade']} |")
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
    p1.add_argument("--tools", default="", help="启用工具，逗号分隔；无则留空")
    p1.add_argument("--permissions", default="unknown", help="权限/沙箱策略快照")
    p1.add_argument("--skills-state", default="unknown",
                    choices=["enabled", "disabled", "unknown", "not_applicable"])
    p1.add_argument("--memory-state", default="unknown",
                    choices=["enabled", "disabled", "unknown", "not_applicable"])
    p1.add_argument("--interface-precheck", default="not_run",
                    choices=["passed", "failed", "not_run", "not_applicable"])

    p2 = sub.add_parser("collect", help="归档产物并判分，写入结果表与证据三件套")
    p2.add_argument("case")
    p2.add_argument("product", choices=PRODUCTS)
    p2.add_argument("--run", type=int, default=1)
    p2.add_argument("--work", required=True)
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
        sys.exit(prepare(a.case, a.product, a.run,
                         root=a.root, variant=a.variant, model=a.model,
                         tools=a.tools, permissions=a.permissions,
                         skills_state=a.skills_state, memory_state=a.memory_state,
                         interface_precheck=a.interface_precheck))
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
                         variant=a.variant, termination=a.termination))


if __name__ == "__main__":
    main()
