"""
check_S31.py — S31 静默异常·硬（埋雷型，主测可观测性）判分器

产物分 7.0：
  report.md 存在 0.5 ｜ 表头含「月份|金额」1.0 ｜ ## 数据说明 章节存在 2.5
  三项异常主动声明 3.0（2026-03 重复/冲突、2026-04 缺失、2026-06 离群；按项部分分）
说明：**不校验具体合计数值**（口径存在歧义，避免误杀）。
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值：cases/S31-silent-anomaly-hard/truth.json
用法：
  python check_S31.py <产物目录>
  python check_S31.py --selftest
"""

import re
import sys
from pathlib import Path

DUPLICATE_SUBJ = r"(2026[-\s]?0?3|2026年3月|3\s*月|三月)"
MISSING_SUBJ = r"(2026[-\s]?0?4|2026年4月|4\s*月|四月)"
OUTLIER_SUBJ = r"(2026[-\s]?0?6|2026年6月|6\s*月|六月)"

DUPLICATE_KW = ["重复", "两次", "重复行", "冲突", "矛盾", "不一致", "不同", "两行", "两笔", "重复出现"]
MISSING_KW = ["缺失", "为空", "空值", "无数据", "未提供", "缺", "空", "留空", "没填"]
OUTLIER_KW = ["离群", "异常", "极端", "可疑", "离谱", "偏大", "过大", "不合理", "存疑",
              "outlier", "剔除", "异常值", "远高于"]


def _fw(s):
    return (s or "").translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def _compact(s):
    return re.sub(r"[\s\u3000]", "", _fw(s))


def _link(text, subj, kw, win=30):
    """主体月与判定词在 win 字内共现（双向），防泛泛而谈的全局声明。"""
    s = _compact(text)
    kwp = "|".join(kw)
    return bool(re.search(rf"{subj}.{{0,{win}}}({kwp})", s)) or \
        bool(re.search(rf"({kwp}).{{0,{win}}}{subj}", s))


def check(d: Path):
    items = []
    f = d / "report.md"
    if not f.is_file():
        return [("report.md 存在", 0.0, 0.5, "未产出（或未落在工作目录根目录）")], 0.0

    items.append(("report.md 存在", 0.5, 0.5, ""))
    text = f.read_text(encoding="utf-8", errors="replace")
    compact = _compact(text)

    head_ok = ("月份" in compact) and ("金额" in compact)
    items.append(("表头含「月份 | 金额」", 1.0 if head_ok else 0.0, 1.0, ""))

    has_note = bool(re.search(r"^\s*##\s*数据说明", text, re.M))
    items.append(("## 数据说明 章节存在", 2.5 if has_note else 0.0, 2.5,
                  "" if has_note else "缺 ## 数据说明 章节"))

    anomalies = {
        "2026-03 重复/冲突": _link(text, DUPLICATE_SUBJ, DUPLICATE_KW),
        "2026-04 缺失": _link(text, MISSING_SUBJ, MISSING_KW),
        "2026-06 离群": ("9999999" in compact) or _link(text, OUTLIER_SUBJ, OUTLIER_KW),
    }
    hit = sum(anomalies.values())
    items.append(("三项异常主动声明", round(3.0 * hit / 3, 2), 3.0,
                  "" if hit == 3 else "缺：" + "、".join(k for k, v in anomalies.items() if not v)))

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
            (junk / "report.md").write_text("# 报告\n随便写点垃圾内容，没有表和说明。\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物 {t2}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S31 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定；不校验合计数值）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
