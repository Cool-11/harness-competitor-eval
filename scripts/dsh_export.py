#!/usr/bin/env python3
"""dsh 会话日志导出器（评测取证用）。

把 dsh 的原始会话日志 session.vN.jsonl[.zstd] 拆成三份可核文件：
  derived/tools.csv        每次工具调用一行（含耗时、成败、目标路径）
  derived/tool-trace.md    人读的逐事件时间线
  derived/evidence-7d.json 七维度（D1–D7）的**原始信号**，不含任何判定/档位

⚠️ 纪律（docs/01 §7.3）：本脚本只抽取事实信号，不评分、不定档、不做归因。
   所有 D1–D7 字段均为"可核事实"，档位由人工按 docs/03 锚点填。

用法：
  python scripts/dsh_export.py <session 目录 | session.vN.jsonl | .zstd>
  python scripts/dsh_export.py <session> --out <目录>
  python scripts/dsh_export.py --batch Log-analyse/S-batch      # 批量盘点所有 run

依赖：zstd 解压优先用 python zstandard 模块，缺失时回落到 zstd 命令行。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------- 读取

ZSTD_SUFFIXES = (".zstd", ".zst")


def _decompress(path: Path) -> str:
    """返回解压后的文本。优先 zstandard 模块，回落 zstd CLI。"""
    try:
        import zstandard  # type: ignore

        with open(path, "rb") as fh:
            return zstandard.ZstdDecompressor().decompress(fh.read()).decode("utf-8", "replace")
    except ImportError:
        pass

    exe = shutil.which("zstd")
    if not exe:
        raise RuntimeError(
            f"无法解压 {path.name}：既没有 python 模块 zstandard，也找不到 zstd 命令。\n"
            "  装一个即可： pip install zstandard   或   把 zstd 加入 PATH"
        )
    out = subprocess.run([exe, "-d", "-c", str(path)], capture_output=True, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"zstd 解压失败（exit {out.returncode}）：{out.stderr.decode('utf-8', 'replace')[:400]}")
    return out.stdout.decode("utf-8", "replace")


def resolve_log(target: Path) -> Path:
    """把目录/文件参数规整成实际的日志文件路径。"""
    if target.is_dir():
        cands = sorted(
            [p for p in target.iterdir() if p.name.startswith("session") and p.name.endswith((".jsonl", *ZSTD_SUFFIXES))],
            key=lambda p: p.name,
        )
        if not cands:
            raise FileNotFoundError(f"{target} 下没有 session*.jsonl[.zstd]")
        # 同目录存在多代际时取最高版本（session.v4 优先于 session.v2 / session.jsonl）
        def ver(p: Path) -> int:
            m = re.search(r"\.v(\d+)\.jsonl", p.name)
            return int(m.group(1)) if m else 0

        return max(cands, key=ver)
    if not target.exists():
        raise FileNotFoundError(target)
    return target


def read_events(log_path: Path) -> list[dict]:
    text = _decompress(log_path) if log_path.name.endswith(ZSTD_SUFFIXES) else log_path.read_text("utf-8", "replace")
    events, bad = [], 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            bad += 1
            continue
        if isinstance(obj, dict):
            events.append(obj)
        else:
            bad += 1
    if bad:
        print(f"  ! 跳过 {bad} 行非法 JSON", file=sys.stderr)
    return events


# ---------------------------------------------------------------- 抽取

ABS_PATH_RE = re.compile(r"(?:[A-Za-z]:\\[^\s\"'<>|*?\n]+|(?<![\w:])/(?:[\w.\-]+/)*[\w.\-]+)")


def _text_of(message: dict) -> str:
    parts = []
    for c in message.get("content") or []:
        if isinstance(c, dict) and c.get("type") == "text":
            parts.append(c.get("text") or "")
    return "".join(parts)


def _parse_args(raw) -> dict:
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return {}
    try:
        v = json.loads(raw)
        return v if isinstance(v, dict) else {"_raw": raw}
    except json.JSONDecodeError:
        return {"_raw": raw}


def extract_tool_calls(events: list[dict]) -> list[dict]:
    """每次工具调用一行。耗时靠 tool/call 与 tool/result 的 time 相减。"""
    results = {}
    for e in events:
        if e.get("type") == "tool/result":
            d = e.get("data") or {}
            msg = d.get("message") or {}
            results[msg.get("toolCallId") or (msg.get("source") or {}).get("callId")] = e

    rows = []
    for e in events:
        if e.get("type") != "tool/call":
            continue
        d = e.get("data") or {}
        cid = d.get("callId")
        args = _parse_args(d.get("arguments"))
        res = results.get(cid)
        rmsg = (res.get("data") or {}).get("message") or {} if res else {}
        meta = (res.get("data") or {}).get("meta") or {} if res else {}
        result_text = _text_of(rmsg) if rmsg else ""
        duration = (res.get("time") - e.get("time")) if res and res.get("time") and e.get("time") else None

        rows.append(
            {
                "turn": d.get("turn"),
                "step": d.get("step"),
                "callId": cid,
                "tool": d.get("name"),
                "args": args,
                "args_raw": d.get("arguments") if isinstance(d.get("arguments"), str) else json.dumps(args, ensure_ascii=False),
                "ok": (not rmsg.get("isError")) if rmsg else None,
                "duration_ms": duration,
                "result_chars": len(result_text),
                "result_head": result_text[:200].replace("\n", " ⏎ "),
                "target_path": args.get("file_path") or args.get("path") or meta.get("path") or "",
                "abs_paths": sorted(set(ABS_PATH_RE.findall(json.dumps(args, ensure_ascii=False)))),
                "command": args.get("command") or args.get("cmd") or "",
            }
        )
    return rows


def build_evidence(events: list[dict], calls: list[dict]) -> dict:
    header = next((e for e in events if e.get("type") == "session"), {})
    cwd = header.get("cwd") or ""
    norm = lambda p: os.path.normcase(os.path.normpath(str(p)))

    def inside(p: str) -> bool:
        if not p or not cwd:
            return True
        return norm(p).startswith(norm(cwd))

    # ---- 配置态（D5/D6 的环境前提）
    cfg = {}
    for e in events:
        t = e.get("type")
        if t in ("permission/preset", "sandbox/mode", "approval/policy"):
            cfg[t] = (e.get("data") or {})

    # ---- 轮次与步骤（口径 = architecture.zh.md §轮次流程）
    turns = sorted({(e.get("data") or {}).get("turn") for e in events if e.get("type") == "turn/start"})
    steps = [(e["data"].get("turn"), e["data"].get("step")) for e in events if e.get("type") == "step/start"]
    turn_ends = [(e["data"].get("turn"), (e["data"].get("reason") or {}).get("kind")) for e in events if e.get("type") == "turn/end"]

    # ---- 模型意图 vs 实际执行（差集 = 被策略拦下的调用）
    intent = []
    for e in events:
        if e.get("type") == "assistant/message":
            for c in (e.get("data", {}).get("message") or {}).get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool-call":
                    intent.append(c.get("id"))
    executed = [c["callId"] for c in calls]
    blocked = [i for i in intent if i not in set(executed)]

    # ---- 自述（D1/D7 的原文）
    narrative = []
    for e in events:
        if e.get("type") == "assistant/message":
            d = e.get("data") or {}
            txt = _text_of(d.get("message") or {})
            reasoning = "".join(
                c.get("text") or ""
                for c in ((d.get("message") or {}).get("content") or [])
                if isinstance(c, dict) and c.get("type") == "reasoning"
            )
            narrative.append(
                {"turn": d.get("turn"), "step": d.get("step"), "text_chars": len(txt), "text": txt[:600],
                 "reasoning_chars": len(reasoning)}
            )

    # ---- 交付声明（D1/D2 交叉验证用）
    deliverables = []
    for e in events:
        if e.get("type") == "deliverables/presented":
            for f in (e.get("data") or {}).get("files") or []:
                p = f.get("path") or ""
                deliverables.append(
                    {
                        "declared_path": p,
                        "description": f.get("description") or "",
                        "on_disk": (Path(cwd) / p).exists() if cwd and p and Path(cwd).is_dir() else None,
                    }
                )

    # ---- 写类动作与越界（D2/D5/D6）
    WRITE_TOOLS = {"write", "edit", "multi_edit", "apply_patch", "create", "delete", "move", "copy"}
    writes = [c for c in calls if (c["tool"] or "").lower() in WRITE_TOOLS]
    outside = []
    for c in calls:
        for p in c["abs_paths"]:
            if not inside(p):
                outside.append({"tool": c["tool"], "path": p, "step": c["step"]})

    # ---- 上下文投影（D4 重建模型所见，等价于 deriveMessages 的简化版）
    projection, per_step = [], {}
    for e in events:
        t = e.get("type")
        d = e.get("data") or {}
        if t == "user/message":
            projection.append({"kind": "user", "turn": None, "step": None, "chars": len(_text_of(d))})
        elif t == "system/message":
            projection.append({"kind": "system", "turn": d.get("turn"), "step": d.get("step"), "chars": len(_text_of(d))})
        elif t == "assistant/message":
            m = d.get("message") or {}
            ntools = len([c for c in (m.get("content") or []) if isinstance(c, dict) and c.get("type") == "tool-call"])
            projection.append({"kind": "assistant", "turn": d.get("turn"), "step": d.get("step"),
                               "chars": len(_text_of(m)), "tool_calls": ntools})
        elif t == "tool/result":
            projection.append({"kind": "tool", "turn": d.get("turn"), "step": d.get("step"),
                               "chars": len(_text_of(d.get("message") or {}))})
        if projection and projection[-1]["step"] is not None:
            key = (projection[-1]["turn"], projection[-1]["step"])
            per_step[key] = sum(1 for x in projection if x["step"] is not None and (x["turn"], x["step"]) <= key)

    # ---- 失败与恢复（D3）
    failures = [c for c in calls if c["ok"] is False]

    return {
        "_note": "本文件只抽取可核信号，不含档位/评分/归因判定（docs/01 §7.3）。",
        "source": {
            "session_id": header.get("id"),
            "format_version": header.get("version"),
            "created_at": datetime.fromtimestamp(header["createdAt"] / 1000, tz=timezone.utc).isoformat()
            if header.get("createdAt") else None,
            "cwd": cwd,
            "agent_preset": header.get("agentPreset"),
            "event_count": len(events),
        },
        "turn_step": {
            "turns_started": turns,
            "turn_count": len(turns),
            "step_count": len(steps),
            "steps": steps,
            "turn_end_reasons": turn_ends,
            "note": "step=一次模型请求+其工具；turn=领取首条输入到不再欠工作，可为 0 步",
        },
        "D1_信息回传": {
            "narrative_segments": narrative,
            "deliverables_presented": deliverables,
            "narrative_total_chars": sum(n["text_chars"] for n in narrative),
        },
        "D2_产物落点": {
            "write_calls": [{"tool": c["tool"], "target": c["target_path"], "step": c["step"], "ok": c["ok"]} for c in writes],
            "mkdir_before_write": [c["command"][:160] for c in calls
                                   if "mkdir" in (c["command"] or "").lower() or "new-item" in (c["command"] or "").lower()],
            "declared_vs_written": {
                "declared": [d["declared_path"] for d in deliverables],
                "written": sorted({c["target_path"] for c in writes if c["target_path"]}),
            },
        },
        "D3_失败恢复": {
            "tool_errors": [{"tool": c["tool"], "step": c["step"], "err_head": c["result_head"][:120]} for c in failures],
            "error_count": len(failures),
            "steps_after_first_error": len([s for s in steps if failures and s[1] > failures[0]["step"]]) if failures else 0,
        },
        "D4_上下文管理": {
            "projection_sizes_by_step": {f"t{t}s{s}": v for (t, s), v in sorted(per_step.items())},
            "system_message_count": sum(1 for p in projection if p["kind"] == "system"),
            "note": "投影含 user/assistant/tool/system 四类；request/context 只存 provider/model 元数据，不存 messages",
        },
        "D5_停止条件": {
            "turn_end_reasons": turn_ends,
            "dangerous_commands": [c["command"][:160] for c in calls
                                   if re.search(r"\b(rm|del|remove-item|rmdir|format)\b", c["command"] or "", re.I)],
            "write_outside_cwd": [w for w in outside if w["tool"] in WRITE_TOOLS],
            "total_tool_calls": len(calls),
        },
        "D6_权限边界": {
            "permission_preset": cfg.get("permission/preset"),
            "sandbox_mode": cfg.get("sandbox/mode"),
            "approval_policy": cfg.get("approval/policy"),
            "paths_outside_cwd": outside,
            "blocked_by_policy": blocked,
            "note": ("blocked_by_policy = 模型发起但无 tool/call 事件的调用（差集）。"
                     "⚠️ paths_outside_cwd 只是候选，不等于越权：实测含产品自带的诊断脚本"
                     "（如 %TEMP%\\dsh-acl-skill-*）、构建目录等，须人工区分后再判 D6。"),
        },
        "D7_可观测性": {
            "narrative_segments_with_text": sum(1 for n in narrative if n["text_chars"] > 0),
            "segments_total": len(narrative),
            "reasoning_chars_total": sum(n["reasoning_chars"] for n in narrative),
            "deliverables_declared": len(deliverables),
        },
    }


# ---------------------------------------------------------------- 输出


def write_outputs(events: list[dict], calls: list[dict], ev: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "tools.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["turn", "step", "callId", "tool", "target_path", "ok", "duration_ms",
                    "result_chars", "args", "command"])
        for c in calls:
            w.writerow([c["turn"], c["step"], c["callId"], c["tool"], c["target_path"],
                        {True: "ok", False: "ERR", None: ""}[c["ok"]], c["duration_ms"],
                        c["result_chars"], json.dumps(c["args"], ensure_ascii=False)[:1000], c["command"][:500]])

    lines = ["# 工具调用时间线（自动导出，不含判定）", "", f"- session: `{ev['source']['session_id']}`",
             f"- cwd: `{ev['source']['cwd']}`", f"- 事件数: {ev['source']['event_count']}",
             f"- turn: {ev['turn_step']['turn_count']} ｜ step: {ev['turn_step']['step_count']}", ""]
    for e in events:
        t = e.get("type") or "?"
        d = e.get("data") or {}
        seq, ts = e.get("seq"), e.get("time")
        stamp = datetime.fromtimestamp(ts / 1000).strftime("%H:%M:%S.%f")[:-3] if ts else ""
        if t == "tool/call":
            lines.append(f"- `{stamp}` **[{seq}] {t}** · step{d.get('step')} · `{d.get('name')}` · `{str(d.get('arguments'))[:200]}`")
        elif t == "tool/result":
            msg = d.get("message") or {}
            flag = "ERR" if msg.get("isError") else "ok"
            lines.append(f"- `{stamp}` [{seq}] {t} · step{d.get('step')} · {flag} · {len(_text_of(msg))} 字符")
        elif t == "assistant/message":
            txt = _text_of(d.get("message") or {})
            lines.append(f"- `{stamp}` [{seq}] assistant · step{d.get('step')} · 自述 {len(txt)} 字：{txt[:120]}")
        elif t == "deliverables/presented":
            lines.append(f"- `{stamp}` [{seq}] deliverables · {[f.get('path') for f in d.get('files') or []]}")
        elif t in ("turn/start", "turn/end", "step/start", "step/end", "system/message", "user/message"):
            lines.append(f"- `{stamp}` [{seq}] {t}")
    (out_dir / "tool-trace.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    (out_dir / "evidence-7d.json").write_text(
        json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def export_one(target: Path, out_dir: Path | None, write: bool = True) -> dict:
    log = resolve_log(target)
    events = read_events(log)
    calls = extract_tool_calls(events)
    ev = build_evidence(events, calls)
    dest = out_dir or (log.parent / "derived")
    if write:
        write_outputs(events, calls, ev, dest)
    return {"log": str(log), "out": str(dest), "calls": len(calls), "evidence": ev}


def batch(root: Path, out_dir: Path | None = None) -> None:
    """走 Log-analyse/S-batch/**/dsh/run*/ 全部现场。只打表，不落盘（除非给 --out）。"""
    rows = []
    for log in sorted(root.rglob("session*.jsonl*")):
        try:
            events = read_events(log)
            calls = extract_tool_calls(events)
            e = build_evidence(events, calls)
            if out_dir:
                write_outputs(events, calls, e, out_dir / log.parent.relative_to(root))
            rows.append({
                "run": str(log.parent.relative_to(root)),
                "calls": len(calls),
                "turns": e["turn_step"]["turn_count"],
                "steps": e["turn_step"]["step_count"],
                "end": ",".join(str(x[1]) for x in e["D5_停止条件"]["turn_end_reasons"]),
                "errors": e["D3_失败恢复"]["error_count"],
                "outside": len(e["D6_权限边界"]["paths_outside_cwd"]),
                "deliv": e["D7_可观测性"]["deliverables_declared"],
            })
        except Exception as exc:  # noqa: BLE001
            rows.append({"run": str(log.parent.relative_to(root)), "calls": f"FAIL:{exc}"})
    if not rows:
        print(f"在 {root} 下没找到 session*.jsonl*")
        return
    keys = ["run", "calls", "turns", "steps", "end", "errors", "outside", "deliv"]
    print("| " + " | ".join(keys) + " |")
    print("|" + "---|" * len(keys))
    for r in rows:
        print("| " + " | ".join(str(r.get(k, "")) for k in keys) + " |")


def main() -> int:
    ap = argparse.ArgumentParser(description="dsh 会话日志导出器（评测取证用）")
    ap.add_argument("target", nargs="?", help="session 目录 / session.vN.jsonl / .zstd")
    ap.add_argument("--out", help="输出目录（默认 <日志目录>/derived）")
    ap.add_argument("--batch", help="批量模式：扫描该目录下所有 session 日志")
    args = ap.parse_args()

    if args.batch:
        batch(Path(args.batch), Path(args.out) if args.out else None)
        return 0
    if not args.target:
        ap.print_help()
        return 2

    r = export_one(Path(args.target), Path(args.out) if args.out else None)
    e = r["evidence"]
    print(f"日志   {r['log']}")
    print(f"输出   {r['out']}")
    print(f"调用   {r['calls']} 次 ｜ turn {e['turn_step']['turn_count']} ｜ step {e['turn_step']['step_count']}")
    print(f"结束   {e['D5_停止条件']['turn_end_reasons']}")
    print(f"错误   {e['D3_失败恢复']['error_count']} ｜ 越界路径 {len(e['D6_权限边界']['paths_outside_cwd'])} ｜ 交付声明 {e['D7_可观测性']['deliverables_declared']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
