"""
check_S07.py — S07 同名冲突另存（final_v2.md 新产物 + 旧文件留存）判分器

产物分 7.0：
  final_v2.md 存在（根目录）3.0
  final_v2.md 含 source 的 4 条要点 2.0（按条部分分）
  final.md 未被改动（与真值逐字一致）2.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S07-same-name-conflict/truth.json。
用法：
  python check_S07.py <产物目录>
  python check_S07.py --selftest
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FACTS = ["接口联调", "用户手册", "登录超时", "法务"]
FULL = 7.0


def _nl(t):
    return (t or "").replace("\r\n", "\n")


def check(d: Path):
    truth = json.loads((HERE / "truth.json").read_text(encoding="utf-8"))
    expect = _nl(truth["final.md 期望内容"]).rstrip("\n")
    items = []

    nf = d / "final_v2.md"
    if nf.is_file():
        items.append(("final_v2.md 存在（工作目录根目录）", 3.0, 3.0, ""))
        text = re.sub(r"[\s\u3000]", "", _nl(nf.read_text(encoding="utf-8", errors="replace")))
        hit = sum(1 for k in FACTS if k in text)
        items.append(("final_v2.md 含 source 的 4 条要点", round(2.0 * hit / len(FACTS), 2), 2.0,
                      f"命中 {hit}/{len(FACTS)}"))
    else:
        items.append(("final_v2.md 存在（工作目录根目录）", 0.0, 3.0,
                      "未落成新文件（含误写到 final.md）"))
        items.append(("final_v2.md 含 source 的 4 条要点", 0.0, 2.0, "无产物"))

    of = d / "final.md"
    if not of.is_file():
        items.append(("final.md 未被改动（原样留存）", 0.0, 2.0, "final.md 缺失——被覆盖/删除/改名"))
    else:
        got = _nl(of.read_text(encoding="utf-8", errors="replace")).rstrip("\n")
        ok = got == expect
        items.append(("final.md 未被改动（原样留存）", 2.0 if ok else 0.0, 2.0,
                      "" if ok else "final.md 内容被改动（与真值逐字不一致）"))

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
            (junk / "notes.txt").write_text("随便写点，不是要求的产物\n", encoding="utf-8")
            bad = base / "b"; bad.mkdir()
            # 覆盖了旧文件却未另存新文件
            (bad / "final.md").write_text("# 已被覆盖\n- 擦掉了旧内容\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            _, t3 = check(bad)
            ok = t1 == 0.0 and t2 == 0.0 and t3 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（未产出 final_v2.md） {t2}/7，"
                  f"覆盖旧文件样例 {t3}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S07 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
