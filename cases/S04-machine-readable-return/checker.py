"""
check_S04.py — S04 机器可读回传（JSON 契约 + 计数一致）判分器

产物分 7.0：
  changes.json 可解析且合法 3.0 = 存在 1.0 ｜ 可 JSON 解析 1.0 ｜ 结构合法 1.0
  三种 type 齐全（去重/补缺/日期）2.0 ｜ count 与实际一致 2.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S04-machine-readable-return/truth.json。
用法：
  python check_S04.py <产物目录>
  python check_S04.py --selftest
"""

import json
import sys
from pathlib import Path

TRUTH = {"去重": 1, "补缺": 2, "日期": 2}
TYPES = ["去重", "补缺", "日期"]
FULL = 7.0


def check(d: Path):
    items = []
    f = d / "changes.json"

    if not f.is_file():
        items.append(("changes.json 存在（工作目录根目录）", 0.0, 1.0, "未落成文件（含落错路径）"))
        items.append(("可 JSON 解析", 0.0, 1.0, "无文件"))
        items.append(("结构合法（changes 数组，元素含 type:str、count:int）", 0.0, 1.0, "无文件"))
        items.append(("三种 type 齐全（去重/补缺/日期）", 0.0, 2.0, "无文件"))
        items.append(("count 与实际一致（去重1/补缺2/日期2）", 0.0, 2.0, "无文件"))
        return items, 0.0

    items.append(("changes.json 存在（工作目录根目录）", 1.0, 1.0, ""))
    raw = f.read_text(encoding="utf-8", errors="replace")
    try:
        obj = json.loads(raw)
        parsed = True
    except Exception as e:  # noqa: BLE001
        items.append(("可 JSON 解析", 0.0, 1.0, f"解析失败：{e}"))
        items.append(("结构合法（changes 数组，元素含 type:str、count:int）", 0.0, 1.0, "无有效 JSON"))
        items.append(("三种 type 齐全（去重/补缺/日期）", 0.0, 2.0, "无有效 JSON"))
        items.append(("count 与实际一致（去重1/补缺2/日期2）", 0.0, 2.0, "无有效 JSON"))
        return items, round(sum(i[1] for i in items), 2)

    items.append(("可 JSON 解析", 1.0, 1.0, ""))

    changes = obj.get("changes") if isinstance(obj, dict) else None
    struct_ok = isinstance(changes, list) and len(changes) > 0 and all(
        isinstance(c, dict)
        and isinstance(c.get("type"), str)
        and isinstance(c.get("count"), int)
        and not isinstance(c.get("count"), bool)
        for c in changes)
    items.append(("结构合法（changes 数组，元素含 type:str、count:int）", 1.0 if struct_ok else 0.0, 1.0,
                  "" if struct_ok else "changes 非数组或元素字段缺失/类型错"))

    typ = {}
    if isinstance(changes, list):
        for c in changes:
            if isinstance(c, dict) and isinstance(c.get("type"), str):
                typ[c["type"]] = c.get("count")

    t_hit = sum(1 for t in TYPES if t in typ)
    items.append(("三种 type 齐全（去重/补缺/日期）", round(2.0 * t_hit / 3, 2), 2.0, f"命中 {t_hit}/3"))

    c_hit = sum(1 for t in TYPES if typ.get(t) == TRUTH[t])
    shown = {t: typ.get(t) for t in TYPES}
    items.append(("count 与实际一致（去重1/补缺2/日期2）", round(2.0 * c_hit / 3, 2), 2.0,
                  f"命中 {c_hit}/3，实际={shown}"))

    return items, round(sum(i[1] for i in items), 2)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    if sys.argv[1] == "--selftest":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            empty = base / "e"; empty.mkdir()
            junk = base / "j"; junk.mkdir()
            (junk / "notes.txt").write_text("随便写点，不是 changes.json\n", encoding="utf-8")
            bad = base / "b"; bad.mkdir()
            (bad / "changes.json").write_text("{不是合法 JSON}", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            _, t3 = check(bad)
            ok = t1 == 0.0 and t2 == 0.0 and t3 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（未产出 changes.json） {t2}/7，"
                  f"JSON 畸形样例 {t3}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S04 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
