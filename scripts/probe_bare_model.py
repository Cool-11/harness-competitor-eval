#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
probe_bare_model.py — U-05 裸模型探针（Tier 0）

目的：把同一题的 prompt 与附件直接交给裸模型（不挂任何产品壳），用同一 checker 判分，
回答"该模型本身能否做对"，为产品分数提供基线参照。

口径（docs/18 U-05）：
  - 同模型 × 2 次，只证明重复性，不证明跨模型泛化；
  - 裸模型不能建目录，产物落点由本脚本代建；因此只测内容，不测路径行为；
  - 原始响应、请求体、判分输出全部落盘，可复核。

用法：
  $env:DEEPSEEK_API_KEY="sk-..."
  python scripts/probe_bare_model.py --task S06 --runs 2
  python scripts/probe_bare_model.py --task S06 --runs 2 --model deepseek-chat
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_ROOT = REPO / "Log-analyse" / "probes" / "U-05-deepseek"

TASKS = {
    "S06": {
        "dir": REPO / "tasks" / "second_tasks" / "S06-artifact-deep-path",
        "attach": "notes.md",
        "artifact": Path("输出") / "汇总" / "月报_v1.md",
    },
}

API_BASE = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
KEY_FILE = REPO / ".secrets" / "deepseek.key"


def get_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key and KEY_FILE.is_file():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    return key


def build_messages(task):
    prompt = (task["dir"] / "prompt.txt").read_text(encoding="utf-8").strip()
    attach_name = task["attach"]
    attach_text = (task["dir"] / "inputs" / attach_name).read_text(encoding="utf-8").strip()
    user = (
        f"{prompt}\n\n"
        f"附件 `{attach_name}` 内容如下：\n\n```\n{attach_text}\n```\n\n"
        "请直接输出目标文件的完整内容，不要解释，不要附加多余文字。"
    )
    return [{"role": "user", "content": user}]


def call_api(model, messages, key, timeout=180):
    body = json.dumps({"model": model, "messages": messages, "stream": False}).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return raw, round(time.time() - t0, 1)


def extract_content(raw):
    data = json.loads(raw)
    content = data["choices"][0]["message"]["content"]
    fence = re.match(r"^\s*```(?:markdown|md)?\s*\n(.*?)\n```\s*$", content, re.S)
    if fence:
        content = fence.group(1)
    return content.strip() + "\n"


def run_checker(task, artifacts):
    checker = task["dir"] / "checker.py"
    proc = subprocess.run(
        [sys.executable, str(checker), str(artifacts)],
        capture_output=True, text=True, encoding="utf-8",
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    m = re.search(r"产物分合计：([\d.]+)/([\d.]+)", output)
    total = float(m.group(1)) if m else None
    return total, output


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="S06", choices=sorted(TASKS))
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--model", default="deepseek-chat")
    args = ap.parse_args()

    key = get_key()
    if not key:
        print("缺少 DeepSeek API key。二选一：")
        print('  1) $env:DEEPSEEK_API_KEY="sk-..."')
        print(f"  2) 把 key 写入 {KEY_FILE}（已由 .gitignore 的 *.key 忽略，不会入库）")
        sys.exit(2)

    task = TASKS[args.task]
    messages = build_messages(task)
    outdir = OUT_ROOT / args.task
    outdir.mkdir(parents=True, exist_ok=True)
    results = []

    for i in range(1, args.runs + 1):
        run = outdir / f"run{i}"
        run.mkdir(parents=True, exist_ok=True)
        print(f"[run{i}] {args.model} → {run}")
        raw, elapsed = call_api(args.model, messages, key)

        (run / "request.json").write_text(
            json.dumps({"model": args.model, "messages": messages}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (run / "response.json").write_text(raw, encoding="utf-8")
        content = extract_content(raw)
        (run / "content.md").write_text(content, encoding="utf-8")

        artifacts = run / "artifacts"
        target = artifacts / task["artifact"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

        total, check_out = run_checker(task, artifacts)
        (run / "check.txt").write_text(check_out, encoding="utf-8")

        usage = json.loads(raw).get("usage", {})
        (run / "score.json").write_text(
            json.dumps({
                "task": args.task,
                "model": args.model,
                "run": i,
                "elapsed_s": elapsed,
                "score": total,
                "full": 7.0,
                "usage": usage,
                "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        results.append((i, total, elapsed, usage))
        print(f"  产物分 {total}/7（{elapsed}s）")

    scores = [r[1] for r in results]
    lines = [
        f"# U-05 裸模型探针 · {args.task} · {args.model}",
        "",
        f"- 时间：{dt.datetime.now().isoformat(timespec='seconds')}",
        f"- 模型：`{args.model}`（DeepSeek 原生 API，无产品壳、无工具、无系统提示）",
        f"- 次数：{args.runs}（同模型）",
        f"- 输入：`{task['dir'].name}/prompt.txt` + `inputs/{task['attach']}` 内联",
        "- 口径：同模型仅证明重复性；路径落点由脚本代建，故不测路径行为",
        "",
        "| run | 产物分 | 耗时(s) | prompt_tokens | completion_tokens |",
        "|---|---:|---:|---:|---:|",
    ]
    for (i, total, elapsed, usage) in results:
        lines.append(
            f"| {i} | {total}/7 | {elapsed} | {usage.get('prompt_tokens', '')} | {usage.get('completion_tokens', '')} |"
        )
    lines += ["", f"**结论候选**：两次均 {'7.0' if all(s == 7.0 for s in scores) else '/'.join(map(str, scores))}。"]
    (outdir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"汇总：{outdir / 'summary.md'}")


if __name__ == "__main__":
    main()
