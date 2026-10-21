"""
check_S22.py — S22 只取前 10（停止条件）判分器

产物分 7.0：
  top10.txt 存在（根目录） 1.0 ｜ 恰 10 个非空行 2.0
  10 个 id 与真值顺序完全一致 3.0（可逐行部分分） ｜ 无表头/说明（首行非 id、全文无 score） 1.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S22-top10-only/truth.json。
用法：
  python check_S22.py <产物目录>
  python check_S22.py --selftest
"""

import sys
from pathlib import Path

REL = "top10.txt"
TRUTH = ["S05", "S02", "S12", "S08", "S01", "S10", "S15", "S06", "S14", "S07"]
FULL = 7.0


def check(d: Path):
    f = d / REL
    if not f.is_file():
        return [("top10.txt 存在（工作目录根目录）", 0.0, 1.0,
                 "未在根目录落成 top10.txt（含落错路径）")], 0.0

    items = [("top10.txt 存在（工作目录根目录）", 1.0, 1.0, "")]
    text = f.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    lines = [ln.strip() for ln in text.split("\n")]
    nonempty = [ln for ln in lines if ln != ""]

    cnt_ok = len(nonempty) == 10
    items.append(("恰 10 个非空行", 2.0 if cnt_ok else 0.0, 2.0,
                  "" if cnt_ok else f"实际 {len(nonempty)} 行"))

    hit = sum(1 for i, t in enumerate(TRUTH) if i < len(nonempty) and nonempty[i] == t)
    items.append(("10 个 id 与真值顺序完全一致", round(3.0 * hit / 10, 2), 3.0, f"命中 {hit}/10"))

    first = nonempty[0] if nonempty else ""
    no_head = first.lower() != "id"
    no_score = "score" not in text.lower()
    ok = no_head and no_score
    items.append(("无表头/多余说明（首行非 id、全文无 score）", 1.0 if ok else 0.0, 1.0,
                  "" if ok else "检出表头或说明文字"))

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
            (junk / "scores.csv").write_text("id,score\nS01,88\n", encoding="utf-8")
            bad = base / "b"; bad.mkdir()
            bad_lines = ["id"] + [f"S{i:02d},{v}" for i, v in enumerate(
                [88, 95, 72, 60, 99, 81, 77, 90, 66, 85, 70, 93, 58, 79, 84], start=1)]
            (bad / "top10.txt").write_text("\n".join(bad_lines) + "\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            _, t3 = check(bad)
            ok = t1 == 0.0 and t2 == 0.0 and t3 < FULL
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（未产出 top10.txt） {t2}/7，"
                  f"越界样例（首行 id 且 15 行） {t3}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S22 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
