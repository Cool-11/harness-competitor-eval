"""
checker.py — S16 多文件汇总基线（5 个小文件，全部读取并汇总）判分器

产物分 7.0：
  summary.md 存在 1.0 ｜ 5 个文件要点全部命中 6.0（每个文件 1.2，按文件内要点比例）
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S16-multifile-baseline/truth.json。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import re
import sys
from pathlib import Path

FILES = {
    "file-01.md": ["星火", "王五", "50万", "进行中"],
    "file-02.md": ["灯塔", "赵六", "70万", "已完成"],
    "file-03.md": ["磐石", "孙七", "90万", "暂停"],
    "file-04.md": ["流云", "周八", "30万", "进行中"],
    "file-05.md": ["青山", "吴九", "60万", "已完成"],
}


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def check(d: Path):
    items = []
    f = d / "summary.md"
    if not f.is_file():
        items.append(("summary.md 存在", 0.0, 1.0, "未落成文件（含落错路径）"))
        items.append(("5 个文件要点全部命中", 0.0, 6.0, "无产物"))
        return items, 0.0
    items.append(("summary.md 存在", 1.0, 1.0, ""))

    c = _compact(f.read_text(encoding="utf-8", errors="replace"))
    total_hits = sum(sum(1 for k in facts if _compact(k) in c) for facts in FILES.values())
    full = sum(len(v) for v in FILES.values())
    detail = " ".join(f"{fn[:7]}={sum(1 for k in fs if _compact(k) in c)}/{len(fs)}"
                      for fn, fs in FILES.items())
    items.append(("5 个文件要点全部命中", round(6.0 * total_hits / full, 2), 6.0, detail))

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
            (junk / "summary.md").write_text("汇总完成，一切正常。\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（空套话） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S16 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
