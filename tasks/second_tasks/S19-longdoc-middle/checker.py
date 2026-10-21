"""
check_S19.py — S19 长文档中段提取（上下文管理）判分器

产物分 7.0：
  extract.md 存在 1.0 ｜ 产品型号 XYZ-300 正确 2.0 ｜ 额定电压 220V 正确 2.0
  保修期 24 个月正确 2.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值：cases/S19-longdoc-middle/truth.json（型号 XYZ-300 / 电压 220V / 保修 24 个月）
      三项事实位于 manual.md 正中间的「技术规格与参数」一节。
用法：
  python check_S19.py <产物目录>
  python check_S19.py --selftest
"""

import re
import sys
from pathlib import Path


def _fw(s):
    return (s or "").translate(str.maketrans(
        "０１２３４５６７８９ＡＢＣＶＸＹＺｘｙｚｖ", "0123456789ABCVXYZxyzv"))


def _compact(s):
    return re.sub(r"[\s\u3000]", "", _fw(s)).lower()


def check(d: Path):
    f = d / "extract.md"
    if not f.is_file():
        return [("extract.md 存在", 0.0, 1.0, "未产出（或未落在工作目录根目录）")], 0.0

    items = [("extract.md 存在", 1.0, 1.0, "")]
    text = _compact(f.read_text(encoding="utf-8", errors="replace"))

    model_ok = ("xyz-300" in text) or ("xyz300" in text)
    items.append(("产品型号 XYZ-300 正确", 2.0 if model_ok else 0.0, 2.0,
                  "" if model_ok else "未见 XYZ-300"))

    volt_ok = "220v" in text
    items.append(("额定电压 220V 正确", 2.0 if volt_ok else 0.0, 2.0,
                  "" if volt_ok else "未见 220V"))

    warranty_ok = ("24个月" in text) or ("24月" in text) or ("24months" in text)
    items.append(("保修期 24 个月正确", 2.0 if warranty_ok else 0.0, 2.0,
                  "" if warranty_ok else "未见 24 个月"))

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
            (junk / "extract.txt").write_text("随便写点别的，不是要求的产物\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 == 0.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（落错路径/文件名） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S19 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
