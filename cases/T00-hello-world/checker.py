"""
check_T00.py — T00 hello-world 校准题判分器
=============================================
checker 是什么：一个独立的自动判分脚本。
  输入：某次运行结束后，产品产出的文件目录
  输出：逐项检查结果 + 0/1 总判定
  约定：exit 0 = 全部通过；exit 1 = 有失败项（借鉴 OpenBench 约定）

用法：
  python check_T00.py <产物目录>

示例：
  python check_T00.py runs/T00/codex/run1/artifacts

判什么（对应 cases/T00-hello-world/task.md 完成条件）：
  1. attendees.md 存在且为文件形态
  2. 含 Markdown 表格，表头含 姓名/单位/职务 三列
  3. 10 行数据，与 inputs/participants.txt 原文一致
  4. 顺序与原文出现顺序一致
"""

import re
import sys
from pathlib import Path

# 预置答案（真值硬编码——注意：本脚本与真值都放在 grading/，
# 投喂产品时只给 inputs/，这就是"真值后注入"防泄漏）
EXPECTED = [
    ("张伟", "华为", "软件工程师"),
    ("李娜", "腾讯", "产品经理"),
    ("王强", "字节跳动", "算法工程师"),
    ("刘洋", "中科院大学", "研究生"),
    ("陈静", "深圳技术大学", "副教授"),
    ("杨帆", "小米", "硬件工程师"),
    ("赵磊", "美团", "后端开发"),
    ("孙悦", "网易", "UI 设计师"),
    ("周涛", "大疆", "嵌入式工程师"),
    ("吴敏", "平安银行", "数据分析师"),
]

HEADER_KEYS = ["姓名", "单位", "职务"]


def parse_markdown_table(text: str):
    """从产物文本中提取第一个 Markdown 表格的数据行（跳过表头和分隔行）。"""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):  # 分隔行
            continue
        if any(k in "".join(cells) for k in HEADER_KEYS) and not rows:
            continue  # 表头行
        rows.append(cells)
    return rows


def check(artifact_dir: Path):
    results = []  # (项名, 通过?, 说明)

    # 1. 文件存在
    target = artifact_dir / "attendees.md"
    if not target.is_file():
        return [("attendees.md 存在", False, f"{target} 不存在——产物未落成文件形态")], 1
    results.append(("attendees.md 存在", True, ""))

    text = target.read_text(encoding="utf-8", errors="replace")

    # 2. 表头三列
    rows = parse_markdown_table(text)
    header_ok = bool(rows) and all(
        any(k in cell for cell in rows[0] for k in [h]) for h in HEADER_KEYS
    )
    # 更稳妥：直接在全文找表头行
    header_ok = all(
        any(h in line for line in text.splitlines() if line.strip().startswith("|"))
        for h in HEADER_KEYS
    )
    results.append(("表头含 姓名/单位/职务 三列", header_ok, "" if header_ok else "未找到含三列的表头行"))

    # 3+4. 数据行逐行对账（顺序敏感）
    data_rows = parse_markdown_table(text)
    # 去掉可能被误吞的表头
    data_rows = [r for r in data_rows if not any(h in "".join(r) for h in HEADER_KEYS)]

    if len(data_rows) != 10:
        results.append(("数据行数 = 10", False, f"实际 {len(data_rows)} 行"))
        return results, 1
    results.append(("数据行数 = 10", True, ""))

    mismatches = []
    for i, (name, org, title) in enumerate(EXPECTED):
        row = data_rows[i]
        joined = "".join(row)
        if not (name in joined and org in joined and title in joined):
            mismatches.append(f"第{i+1}行应为 {name}/{org}/{title}，实际 {'/'.join(row)}")
    if mismatches:
        results.append(("10 行内容与原文一致且顺序正确", False, "；".join(mismatches)))
        return results, 1
    results.append(("10 行内容与原文一致且顺序正确", True, ""))

    return results, 0


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    artifact_dir = Path(sys.argv[1])

    # —— 负控制自测：checker 自身要先证明"垃圾产物判不过" ——
    # 用法：python check_T00.py --selftest
    if str(artifact_dir) == "--selftest":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "empty"
            empty.mkdir()
            r1, c1 = check(empty)
            junk = Path(td) / "junk"
            junk.mkdir()
            (junk / "attendees.md").write_text("这是一个完全无关的产物 12345", encoding="utf-8")
            r2, c2 = check(junk)
            ok = c1 == 1 and c2 == 1
            print(f"负控制自测：空目录判 {c1}，垃圾产物判 {c2} → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    results, code = check(artifact_dir)
    print(f"# T00 判分 · {artifact_dir}")
    for name, ok, note in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {note}" if note else ""))
    total_pass = sum(1 for _, ok, _ in results if ok)
    print(f"合计：{total_pass}/{len(results)} 项通过 → 判定 {'通过(0)' if code == 0 else '不通过(1)'}")
    sys.exit(code)


if __name__ == "__main__":
    main()
