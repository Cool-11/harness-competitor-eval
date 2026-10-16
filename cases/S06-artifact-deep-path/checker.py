"""
check_S06.py — S06 产物落点（深路径 + 中文目录 + 编码）判分器

产物分 7.0：
  输出/汇总/月报_v1.md 存在 2.0 ｜ 首个非空行 == # 九月月报 1.5
  UTF-8 合法 1.0 ｜ 6 条事项齐全 2.5
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S06-artifact-deep-path/truth.json。
用法：
  python check_S06.py <产物目录>
  python check_S06.py --selftest
"""

import re
import sys
from pathlib import Path

REL = ("输出", "汇总", "月报_v1.md")
FACTS = ["v0.3", "8 秒", "2 秒", "6 人", "供应商 B", "移动端适配"]


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def check(d: Path):
    items = []
    f = d / REL[0] / REL[1] / REL[2]
    if not f.is_file():
        return [("输出/汇总/月报_v1.md 存在", 0.0, 2.0, "未在该路径落成文件（含落根目录）")], 0.0
    items.append(("输出/汇总/月报_v1.md 存在", 2.0, 2.0, ""))

    raw = f.read_bytes()
    try:
        text = raw.decode("utf-8")
        enc_ok = True
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")
        enc_ok = False
    items.append(("UTF-8 合法", 1.0 if enc_ok else 0.0, 1.0, "" if enc_ok else "非 UTF-8"))

    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    head_ok = first == "# 九月月报"
    items.append(("首个非空行 == # 九月月报", 1.5 if head_ok else 0.0, 1.5,
                  "" if head_ok else f"实际首行：{first[:30]}"))

    compact = _compact(text)
    hit = sum(1 for k in FACTS if _compact(k) in compact)
    items.append(("6 条事项齐全（无遗漏/增补）", round(2.5 * hit / 6, 2), 2.5,
                  f"命中 {hit}/6"))

    return items, round(sum(i[1] for i in items), 2)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    if sys.argv[1] == "--selftest":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "e"; empty.mkdir()
            junk = Path(td) / "j"; junk.mkdir()
            (junk / "月报_v1.md").write_text("# 别的标题\n随便写点\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 == 0.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（落错路径） {t2}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S06 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
