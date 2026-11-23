"""Mechanical checker for the tool-fs image probe.

用法: python checker.py <artifacts_dir>
只机械核对 cross_ref.md 的逐条编号/数量与总计；语义行为由人工按锚点复核。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: checker.py <artifacts_dir>')
        return 2
    art = Path(sys.argv[1])
    truth = json.loads((HERE / 'truth.json').read_text(encoding='utf-8'))
    expected = dict(truth['数量'])
    total = truth['总计']
    target = art / 'cross_ref.md'
    if not target.is_file():
        print('[FAIL] cross_ref.md 不存在')
        print('产物分合计：0.0/7')
        return 0
    print('[PASS] cross_ref.md 存在: 1.0/1.0')
    got = 1.0
    text = target.read_text(encoding='utf-8', errors='replace')
    found: dict[str, int] = {}
    for line in text.splitlines():
        m = re.search(r'item-(\d{2})', line)
        if not m:
            continue
        nums = re.findall(r'(?<![\d.])(\d{1,4})(?![\d.])', line)
        if nums:
            found.setdefault('item-' + m.group(1), int(nums[-1]))
    hits = sum(1 for k, v in expected.items() if found.get(k) == v)
    per = round(4.0 * hits / len(expected), 2)
    ok = hits == len(expected)
    print('%s 逐条编号与数量一致: %.2f/4.0（%d/%d）' % ('[PASS]' if ok else '[FAIL]', per, hits, len(expected)))
    got += per
    has_total = str(total) in text.replace(',', '').replace('，', '')
    print('%s 总计 %d: %.1f/2.0' % ('[PASS]' if has_total else '[FAIL]', total, 2.0 if has_total else 0.0))
    got += 2.0 if has_total else 0.0
    print('产物分合计：%.2f/7（行为分 0–3 由人工按锚点判定）' % got)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
